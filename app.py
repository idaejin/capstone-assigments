"""
Streamlit web application for Student-Project Allocation Matching Algorithm.
"""

import streamlit as st
import pandas as pd
import io
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data_loader import load_students, load_projects, load_supervisors, Student, Project, Supervisor
from src.spa_algorithm import SPAStudentAlgorithm
from evaluation.metrics import MatchingEvaluator
from evaluation.visualizations import plot_satisfaction_distribution, plot_matching_summary
import matplotlib.pyplot as plt


# Page configuration
st.set_page_config(
    page_title="Student-Project Allocation",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def show_data_statistics(students, projects, supervisors):
    """Display statistics about loaded data."""
    st.markdown("---")
    st.subheader("📊 Data Statistics")
    
    # Student statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(students))
    
    with col2:
        st.metric("Total Topics", len(projects))
    
    with col3:
        st.metric("Total Supervisors", len(supervisors))
    
    with col4:
        # Topics have no capacity limit - only supervisor capacity matters
        st.metric("Topics", len(projects))
    
    # Program breakdown
    st.markdown("#### 🎓 Students by Program")
    program_counts = {}
    for sid in students.keys():
        if sid.startswith('BDBA') and not sid.startswith('BBA_BDBA'):
            program_counts['BDBA'] = program_counts.get('BDBA', 0) + 1
        elif sid.startswith('BCSAI'):
            program_counts['BCSAI'] = program_counts.get('BCSAI', 0) + 1
        elif sid.startswith('BBA_BDBA'):
            program_counts['BBA+BDBA'] = program_counts.get('BBA+BDBA', 0) + 1
        elif sid.startswith('BBA') and not sid.startswith('BBA_'):
            program_counts['BBA'] = program_counts.get('BBA', 0) + 1
        else:
            program_counts['Other'] = program_counts.get('Other', 0) + 1
    
    if program_counts:
        program_df = pd.DataFrame(list(program_counts.items()), columns=['Program', 'Count'])
        st.dataframe(program_df, use_container_width=True, hide_index=True)
    
    # Topics by area
    st.markdown("#### 📚 Topics by Area")
    area_counts = {}
    for topic in projects.values():
        area = topic.area
        area_counts[area] = area_counts.get(area, 0) + 1
    
    if area_counts:
        area_df = pd.DataFrame(list(area_counts.items()), columns=['Area', 'Number of Topics'])
        st.dataframe(area_df, use_container_width=True, hide_index=True)
    
    # Topic statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👨‍🏫 Topics by Supervisor")
        # Build supervisor-topic mapping from supervisor preferences
        supervisor_topics = {}
        for sup_id, supervisor in supervisors.items():
            # Get unique topics for this supervisor (across all bachelors)
            topics = set()
            for (bachelor, topic_id) in supervisor.bachelor_topic_expertise.keys():
                topics.add(topic_id)
            supervisor_topics[sup_id] = list(topics)
        
        sup_stats = []
        for sup_id, topic_list in supervisor_topics.items():
            if topic_list:
                # Topics have no capacity limit - only supervisor capacity matters
                # Get all expertise levels for this supervisor
                expertise_levels = list(supervisors[sup_id].bachelor_topic_expertise.values())
                max_cap = supervisors[sup_id].capacity if sup_id in supervisors else 'N/A'
                sup_stats.append({
                    'Supervisor': sup_id,
                    'Topics': len(topic_list),  # Number of topics (no limit, minimum 1)
                    'Max Capacity': f"{max_cap}/10" if isinstance(max_cap, int) else max_cap,  # Show as X/10 to indicate max limit
                    'Expertise Levels': ', '.join(set(expertise_levels))
                })
        
        if sup_stats:
            sup_df = pd.DataFrame(sup_stats)
            st.dataframe(sup_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 📊 Topic Statistics")
        
        # Topics by area
        area_dist = {}
        for project in projects.values():
            area_dist[project.area] = area_dist.get(project.area, 0) + 1
        
        st.markdown("**Topics by Area:**")
        for area, count in sorted(area_dist.items()):
            st.write(f"- {area}: {count} topics")
        
        # Expertise level distribution (from supervisors)
        expertise_dist = {}
        for supervisor in supervisors.values():
            for level in supervisor.bachelor_topic_expertise.values():
                expertise_dist[level] = expertise_dist.get(level, 0) + 1
        
        if expertise_dist:
            st.markdown("**Expertise Level Distribution:**")
            for level, count in sorted(expertise_dist.items()):
                st.write(f"- {level}: {count} topics")
        
        # Average preferences per student (always 5 now)
        avg_prefs = sum(len(s.preferences) for s in students.values()) / len(students) if students else 0
        st.metric("Avg Preferences per Student", f"{avg_prefs:.1f} (required: 5)")
    
    # Capacity analysis
    st.markdown("#### 💼 Capacity Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_supervisor_capacity = sum(s.capacity for s in supervisors.values())
        st.metric("Total Supervisor Capacity", total_supervisor_capacity)
    
    with col2:
        # Topics have no capacity limit - only supervisor capacity matters
        st.metric("Total Topics", len(projects))
    
    with col3:
        capacity_ratio = (len(students) / total_supervisor_capacity * 100) if total_supervisor_capacity > 0 else 0
        st.metric("Capacity Utilization", f"{capacity_ratio:.1f}%")
    
    # Warning if supervisor capacity is insufficient
    if total_supervisor_capacity < len(students):
        st.warning(f"⚠️ Total supervisor capacity ({total_supervisor_capacity}) is less than number of students ({len(students)}). Some students may not be matched.")
    else:
        st.success(f"✅ Supervisor capacity ({total_supervisor_capacity}) is sufficient for {len(students)} students.")


def parse_text_input(text: str, input_type: str):
    """Parse text input into data structures."""
    # Filter out comments and empty lines
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            lines.append(line)
    
    if input_type == "students":
        students = {}
        for line in lines:
            if ':' in line:
                parts = line.split(':')
                student_id = parts[0].strip()
                prefs = [p.strip() for p in parts[1].split(',') if p.strip()]
                # Validate: exactly 5 preferences required
                if len(prefs) != 5:
                    raise ValueError(f"Student {student_id} has {len(prefs)} preferences (exactly 5 required)")
                students[student_id] = Student(student_id, prefs)
        return students
    
    elif input_type == "projects":
        projects = {}
        for line in lines:
            if ':' in line:
                parts = line.split(':')
                project_id = parts[0].strip()
                details = [d.strip() for d in parts[1].split(',')]
                if len(details) >= 1:
                    area = details[0]
                    projects[project_id] = Project(project_id, area)
        return projects
    
    elif input_type == "supervisors":
        supervisors = {}
        for line in lines:
            if ':' in line:
                # Split only on the first colon to separate supervisor_id from the rest
                first_colon_idx = line.find(':')
                supervisor_id = line[:first_colon_idx].strip()
                rest = line[first_colon_idx + 1:].strip()
                
                # Split the rest by comma
                details = [d.strip() for d in rest.split(',')]
                if len(details) >= 1:
                    capacity = int(details[0])
                    if capacity > 10:
                        raise ValueError(f"Supervisor {supervisor_id} has capacity {capacity}, maximum allowed is 10")
                    
                    # Parse bachelor:topic:expertise triples
                    bachelor_topic_expertise = {}
                    for item in details[1:]:
                        if item.count(':') == 2:  # Format: Bachelor:TopicID:ExpertiseLevel
                            bachelor, topic_id, expertise_level = item.split(':', 2)
                            bachelor = bachelor.strip()
                            topic_id = topic_id.strip()
                            expertise_level = expertise_level.strip()
                            bachelor_topic_expertise[(bachelor, topic_id)] = expertise_level
                        else:
                            raise ValueError(f"Supervisor {supervisor_id} has invalid format '{item}'. Expected: Bachelor:TopicID:ExpertiseLevel")
                    
                    # Validate: Supervisor must have at least 1 bachelor-topic combination
                    if len(bachelor_topic_expertise) < 1:
                        raise ValueError(f"Supervisor {supervisor_id} must have at least 1 bachelor-topic combination")
                    
                    supervisors[supervisor_id] = Supervisor(supervisor_id, capacity, bachelor_topic_expertise)
        return supervisors
    
    return {}


def main():
    st.markdown('<div class="main-header">🎓 Student-Project Allocation Matching Algorithm</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Navigation")
        page = st.radio(
            "Choose a page",
            ["Home", "Input Data", "Run Algorithm", "Results & Analysis", "About"]
        )
    
    if page == "Home":
        show_home_page()
    elif page == "Input Data":
        show_input_page()
    elif page == "Run Algorithm":
        show_algorithm_page()
    elif page == "Results & Analysis":
        show_results_page()
    elif page == "About":
        show_about_page()


def show_home_page():
    """Display home page with overview."""
    st.header("Welcome to the Student-Project Allocation System")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Algorithm", "SPA-Student", "Abraham et al. 2007")
    
    with col2:
        st.metric("Features", "Stable Matching", "Capacity Constraints")
    
    with col3:
        st.metric("Evaluation", "Multiple Metrics", "Visualizations")
    
    st.markdown("---")
    
    st.subheader("How It Works")
    
    st.markdown("""
    This application implements the **SPA-student algorithm** for allocating students to capstone projects.
    
    ### Key Features:
    
    1. **Stable Matching**: Ensures no student-project pair would prefer each other over their current assignment
    2. **Capacity Constraints**: Respects supervisor capacity limits (topics have no capacity limit)
    3. **Preference-Based**: Considers preferences from both students and supervisors
    4. **Comprehensive Evaluation**: Provides detailed metrics and visualizations
    
    ### Quick Start:
    
    1. Go to **Input Data** to enter or upload your data
    2. Navigate to **Run Algorithm** to execute the matching
    3. View **Results & Analysis** for detailed evaluation
    
    ### Input Format:
    
    - **Students**: `StudentID: Topic1, Topic2, Topic3, ...`
    - **Topics/Projects**: `TopicID: Area` (no capacity limit)
    - **Supervisors**: `SupervisorID: MaximumCapacity, Student1, Student2, ...`
    
    **Note:** Supervisor capacity represents the maximum total number of students a supervisor can handle across all topics.
    """)


def show_input_page():
    """Display input data page."""
    st.header("📥 Input Data")
    
    input_method = st.radio(
        "Choose input method",
        ["Manual Entry", "File Upload", "Use Example Data"],
        horizontal=True
    )
    
    if input_method == "Manual Entry":
        show_manual_input()
    elif input_method == "File Upload":
        show_file_upload()
    else:
        show_example_data()


def show_manual_input():
    """Show manual text input fields."""
    st.subheader("Enter Data Manually")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Students")
        students_text = st.text_area(
            "Student preferences (one per line)",
            value="BDBA001: T01, T02, T03, T04, T05\nBCSAI001: T01, T02, T03, T04, T05\nBBA_BDBA001: T01, T02, T03, T04, T05",
            height=200,
            help="Format: StudentID: Topic1, Topic2, Topic3, Topic4, Topic5 (exactly 5 preferences required)"
        )
    
    with col2:
        st.markdown("### Topics/Projects")
        projects_text = st.text_area(
            "Topic/Project information (one per line)",
            value="T01: Data Science\nT02: Data Science\nT03: Machine Learning\nT04: Machine Learning\nT05: Computer Science",
            height=200,
            help="Format: TopicID: Area (topics have no capacity limit). Optional: TopicID: Area, Student1, Student2, ... for topic preferences"
        )
    
    st.markdown("### Supervisors")
    supervisors_text = st.text_area(
        "Supervisor information (one per line)",
        value="SUP01: 5, BDBA:T01:Expert, BDBA:T03:Advanced, BDBA:T05:Intermediate\nSUP02: 4, BCSAI:T02:Expert, BCSAI:T04:Advanced, BBA+BDBA:T01:Expert",
        height=150,
        help="Format: SupervisorID: MaximumCapacity (max 10), Bachelor1:Topic1:ExpertiseLevel1, Bachelor1:Topic2:ExpertiseLevel2, ..."
    )
    
    if st.button("💾 Save Input Data", type="primary"):
        try:
            students = parse_text_input(students_text, "students")
            projects = parse_text_input(projects_text, "projects")
            supervisors = parse_text_input(supervisors_text, "supervisors")
            
            # Validate
            if not students or not projects or not supervisors:
                st.error("Please provide valid data for all three categories.")
                return
            
            # Store in session state
            st.session_state['students'] = students
            st.session_state['projects'] = projects
            st.session_state['supervisors'] = supervisors
            st.session_state['students_text'] = students_text
            st.session_state['projects_text'] = projects_text
            st.session_state['supervisors_text'] = supervisors_text
            
            st.success(f"✅ Data saved! ({len(students)} students, {len(projects)} projects, {len(supervisors)} supervisors)")
            
            # Show statistics
            show_data_statistics(students, projects, supervisors)
            
            # Show preview
            with st.expander("📊 Preview Data"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Students:**")
                    for sid, student in list(students.items())[:5]:
                        st.write(f"{sid}: {', '.join(student.preferences[:3])}...")
                
                with col2:
                    st.write("**Topics:**")
                    for pid, project in list(projects.items())[:5]:
                        st.write(f"{pid}: {project.area} (no capacity limit)")
                
                with col3:
                    st.write("**Supervisors:**")
                    for sid, supervisor in list(supervisors.items())[:5]:
                        num_combinations = len(supervisor.bachelor_topic_expertise)
                        st.write(f"{sid}: cap={supervisor.capacity}, {num_combinations} topic combinations")
        
        except Exception as e:
            st.error(f"Error parsing data: {str(e)}")


def show_file_upload():
    """Show file upload interface."""
    st.subheader("Upload Data Files")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        students_file = st.file_uploader("Students File", type=['txt'], help="Format: StudentID: Project1, Project2, ...")
    
    with col2:
        projects_file = st.file_uploader("Projects File", type=['txt'], help="Format: ProjectID: SupervisorID, Capacity")
    
    with col3:
        supervisors_file = st.file_uploader("Supervisors File", type=['txt'], help="Format: SupervisorID: Capacity, Student1, ...")
    
    if st.button("📤 Load Files", type="primary"):
        if students_file and projects_file and supervisors_file:
            try:
                students_text = students_file.read().decode('utf-8')
                projects_text = projects_file.read().decode('utf-8')
                supervisors_text = supervisors_file.read().decode('utf-8')
                
                students = parse_text_input(students_text, "students")
                projects = parse_text_input(projects_text, "projects")
                supervisors = parse_text_input(supervisors_text, "supervisors")
                
                st.session_state['students'] = students
                st.session_state['projects'] = projects
                st.session_state['supervisors'] = supervisors
                st.session_state['students'] = students
                st.session_state['projects'] = projects
                st.session_state['supervisors'] = supervisors
                st.session_state['students_text'] = students_text
                st.session_state['projects_text'] = projects_text
                st.session_state['supervisors_text'] = supervisors_text
                
                st.success(f"✅ Files loaded! ({len(students)} students, {len(projects)} projects, {len(supervisors)} supervisors)")
                
                # Show statistics
                show_data_statistics(students, projects, supervisors)
            
            except Exception as e:
                st.error(f"Error loading files: {str(e)}")
        else:
            st.warning("Please upload all three files.")


def show_example_data():
    """Show example data and load it."""
    st.subheader("Example Data")
    
    # Load example data from files if they exist
    try:
        with open("data/students.txt", "r") as f:
            example_students_full = f.read()
            # Process and limit to 5 preferences per student
            lines = example_students_full.split('\n')
            example_students_lines = []
            for line in lines:
                if ':' in line and not line.strip().startswith('#'):
                    parts = line.split(':')
                    if len(parts) == 2:
                        student_id = parts[0].strip()
                        prefs = [p.strip() for p in parts[1].split(',') if p.strip()][:5]  # Limit to 5
                        if len(prefs) > 0:
                            example_students_lines.append(f"{student_id}: {', '.join(prefs)}")
            example_students = '\n'.join(example_students_lines[:15])  # Show first 15 students
        
        with open("data/topics.txt", "r") as f:
            example_projects = f.read()
        with open("data/supervisors.txt", "r") as f:
            example_supervisors = f.read()
    except FileNotFoundError:
        # Fallback to simple example (all topics referenced must exist)
        example_students = """BDBA001: T01, T02, T03, T04, T05
BCSAI001: T01, T02, T03, T04, T05
BBA_BDBA001: T01, T02, T03, T04, T05"""
        
        example_projects = """T01: Data Science
T02: Data Science
T03: Machine Learning
T04: Machine Learning
T05: Computer Science"""
        
        example_supervisors = """SUP01: 5, BDBA:T01:Expert, BDBA:T03:Advanced, BDBA:T05:Intermediate
SUP02: 4, BCSAI:T02:Expert, BCSAI:T04:Advanced, BBA+BDBA:T01:Expert
SUP03: 5, BDBA:T02:Advanced, BCSAI:T03:Intermediate, BBA+BDBA:T05:Expert"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.text_area("Students (BDBA, BCSAI, BBA+BDBA)", example_students, height=200, disabled=True)
    
    with col2:
        st.text_area("Topics/Projects (with Areas)", example_projects, height=200, disabled=True)
    
    with col3:
        st.text_area("Supervisors (Topics with Expertise)", example_supervisors, height=200, disabled=True)
    
    if st.button("📋 Load Example Data", type="primary"):
        # Load full data from files, not truncated display
        try:
            with open("data/students.txt", "r") as f:
                full_students_text = f.read()
            with open("data/topics.txt", "r") as f:
                full_projects_text = f.read()
            with open("data/supervisors.txt", "r") as f:
                full_supervisors_text = f.read()
            
            students = parse_text_input(full_students_text, "students")
            projects = parse_text_input(full_projects_text, "projects")
            supervisors = parse_text_input(full_supervisors_text, "supervisors")
            
            # Store full text for display
            students_text = full_students_text
            projects_text = full_projects_text
            supervisors_text = full_supervisors_text
        except FileNotFoundError:
            # Fallback to displayed example data if files not found
            students = parse_text_input(example_students, "students")
            projects = parse_text_input(example_projects, "projects")
            supervisors = parse_text_input(example_supervisors, "supervisors")
            
            students_text = example_students
            projects_text = example_projects
            supervisors_text = example_supervisors
        
        st.session_state['students'] = students
        st.session_state['projects'] = projects
        st.session_state['supervisors'] = supervisors
        st.session_state['students_text'] = students_text
        st.session_state['projects_text'] = projects_text
        st.session_state['supervisors_text'] = supervisors_text
        
        st.success("✅ Example data loaded!")
        
        # Show statistics
        show_data_statistics(students, projects, supervisors)


def show_algorithm_page():
    """Display algorithm execution page."""
    st.header("⚙️ Run Matching Algorithm")
    
    # Check if data is loaded
    if 'students' not in st.session_state:
        st.warning("⚠️ No data loaded. Please go to 'Input Data' page first.")
        return
    
    students = st.session_state['students']
    projects = st.session_state['projects']
    supervisors = st.session_state['supervisors']
    
    # Count students by program
    bdba_count = sum(1 for sid in students if sid.startswith('BDBA') and not sid.startswith('BBA_BDBA'))
    bcsai_count = sum(1 for sid in students if sid.startswith('BCSAI'))
    bba_bdba_count = sum(1 for sid in students if sid.startswith('BBA_BDBA'))
    
    program_breakdown = []
    if bdba_count > 0:
        program_breakdown.append(f"{bdba_count} BDBA")
    if bcsai_count > 0:
        program_breakdown.append(f"{bcsai_count} BCSAI")
    if bba_bdba_count > 0:
        program_breakdown.append(f"{bba_bdba_count} BBA+BDBA")
    
    programs_str = ", ".join(program_breakdown) if program_breakdown else "various programs"
    st.info(f"📊 Ready to process: {len(students)} students ({programs_str}), {len(projects)} topics, {len(supervisors)} supervisors")
    
    with st.expander("ℹ️ What happens when I run the algorithm?"):
        st.markdown("""
        **The SPA-Student Algorithm Process (Sequential Rounds):**
        
        **Round 1:**
        1. **Initialization**: Each student applies to their most preferred topic
        2. **Evaluation**: Topics evaluate applications based on supervisor preferences
        3. **Acceptance/Rejection**: Topics accept students based on supervisor capacity (topics have no capacity limit)
        4. **Reapplication**: Rejected students apply to their next preferred topic
        5. **Iteration**: Process continues until no more applications or all students matched
        
        **Round 2+ (if needed):**
        - Unmatched students continue with their remaining untried preferences
        - Process repeats until all students matched or no new matches occur
        
        **Final Steps:**
        - Stability Check: Algorithm ensures no blocking pairs exist
        - Constraint Verification: All capacity limits are respected
        
        **What You'll Get:**
        - Maximum number of matches (sequential rounds maximize matching)
        - A stable matching (if possible)
        - All capacity constraints respected
        - Optimal balance between student and supervisor preferences
        
        **Time Complexity**: O(n²) where n is the number of students
        """)
    
    # Full-width button
    if st.button("🚀 Run Algorithm", type="primary", use_container_width=True):
        with st.spinner("Running matching algorithm..."):
            try:
                # Initialize and run algorithm
                algorithm = SPAStudentAlgorithm(students, projects, supervisors)
                results = algorithm.run()
                
                # Store results
                st.session_state['algorithm'] = algorithm
                st.session_state['results'] = algorithm.get_results()
                st.session_state['matching_complete'] = True
                
                # Get round statistics
                round_stats = algorithm.get_round_statistics()
                st.session_state['round_stats'] = round_stats
                
                st.success(f"✅ Matching completed in {round_stats['total_rounds']} round(s)!")
                
                # Show quick summary with interpretation
                matched = sum(1 for r in st.session_state['results'] if r['ProjectID'] is not None)
                match_rate = matched/len(students)*100
                
                # Display round information
                if round_stats['total_rounds'] > 0:
                    st.info(f"📊 **Matching Rounds**: {round_stats['total_rounds']} round(s) executed")
                    round_info = []
                    for round_num in sorted(round_stats['round_counts'].keys()):
                        count = round_stats['round_counts'][round_num]
                        round_info.append(f"Round {round_num}: {count} students matched")
                    st.markdown("  • " + "  • ".join(round_info))
                
                # Full-width metrics display
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                
                with metrics_col1:
                    st.metric("Students Matched", f"{matched}/{len(students)}", f"{match_rate:.1f}%")
                
                with metrics_col2:
                    # Calculate average student rank
                    ranks = [r['StudentRank'] for r in st.session_state['results'] if r['StudentRank'] is not None]
                    avg_rank = sum(ranks) / len(ranks) if ranks else None
                    if avg_rank:
                        st.metric("Avg Satisfaction", f"Rank {avg_rank:.2f}", 
                                 "Lower is better")
                
                with metrics_col3:
                    # Check stability
                    is_stable = algorithm.is_stable()
                    st.metric("Stability", "✅ Stable" if is_stable else "⚠️ Check", 
                             "Optimal matching" if is_stable else "Review needed")
                
                # Interpretation
                if match_rate >= 90:
                    st.success(f"🎉 **Excellent!** {match_rate:.1f}% of students matched. Most students have been successfully assigned to topics.")
                elif match_rate >= 70:
                    st.info(f"✅ **Good!** {match_rate:.1f}% of students matched. Most students have been assigned, but some remain unmatched.")
                elif match_rate >= 50:
                    st.warning(f"⚠️ **Fair.** {match_rate:.1f}% of students matched. Consider reviewing capacities or adding more topics.")
                else:
                    st.error(f"❌ **Low match rate.** Only {match_rate:.1f}% of students matched. Significant issues with capacity or preferences.")
                
                st.info("💡 **Next Step**: Go to 'Results & Analysis' page for detailed metrics and improvement suggestions.")
            
            except Exception as e:
                st.error(f"Error running algorithm: {str(e)}")
                st.exception(e)
    
    # Show current matching if available
    if 'matching_complete' in st.session_state and st.session_state['matching_complete']:
        st.markdown("---")
        st.subheader("📋 Current Matching Results")
        
        results_df = pd.DataFrame(st.session_state['results'])
        results_df = results_df[results_df['ProjectID'].notna()]
        
        if not results_df.empty:
            # Add program column for better visualization
            display_df = results_df.copy()
            display_df['Program'] = display_df['StudentID'].apply(
                lambda x: 'BDBA' if x.startswith('BDBA') and not x.startswith('BBA_BDBA') 
                else 'BCSAI' if x.startswith('BCSAI') 
                else 'BBA+BDBA' if x.startswith('BBA_BDBA') 
                else 'Other'
            )
            
            # Reorder columns
            base_cols = ['StudentID', 'Program', 'ProjectID', 'Area', 'SupervisorID', 'ExpertiseLevel', 'StudentRank', 'MatchingRound']
            display_df = display_df[base_cols]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results (CSV)",
                data=csv,
                file_name="matching_results.csv",
                mime="text/csv"
            )
        else:
            st.warning("No matches found.")


def show_results_page():
    """Display results and analysis page."""
    st.header("📊 Results & Analysis")
    
    if 'matching_complete' not in st.session_state or not st.session_state['matching_complete']:
        st.warning("⚠️ Please run the algorithm first on the 'Run Algorithm' page.")
        return
    
    algorithm = st.session_state['algorithm']
    results = st.session_state['results']
    
    # Get data from session state or algorithm
    students = st.session_state.get('students', algorithm.students)
    projects = st.session_state.get('projects', algorithm.projects)
    supervisors = st.session_state.get('supervisors', algorithm.supervisors)
    
    # Create evaluator
    evaluator = MatchingEvaluator(algorithm)
    report = evaluator.generate_full_report()
    
    # Key Metrics with explanations
    st.subheader("📈 Key Metrics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        stability = report['stability']
        status = "✅ Stable" if stability['is_stable'] else "❌ Unstable"
        st.metric(
            "Stability",
            status,
            f"{stability['blocking_pairs']} blocking pairs"
        )
        with st.expander("ℹ️ What is Stability?"):
            st.markdown("""
            **Stable Matching** means no student-topic pair would prefer each other over their current assignment.
            
            - ✅ **Stable**: The matching is optimal - no improvements possible
            - ❌ **Unstable**: Some students/topics could be better matched
            - **Blocking Pairs**: Number of student-topic pairs that would prefer each other
            
            **Interpretation:**
            - 0 blocking pairs = Perfect stability
            - Few blocking pairs = Good matching
            - Many blocking pairs = Consider adjusting preferences or capacities
            """)
    
    with col2:
        efficiency = report['efficiency']
        match_rate = efficiency['student_match_rate']*100
        st.metric(
            "Match Rate",
            f"{match_rate:.1f}%",
            f"{efficiency['matched_students']}/{efficiency['total_students']} students"
        )
        with st.expander("ℹ️ What is Match Rate?"):
            st.markdown(f"""
            **Match Rate** shows what percentage of students were successfully assigned to topics.
            
            **Current Result:** {match_rate:.1f}% ({efficiency['matched_students']} out of {efficiency['total_students']} students)
            
            **Interpretation:**
            - **90-100%**: Excellent - Almost all students matched
            - **70-89%**: Good - Most students matched
            - **50-69%**: Fair - Some students unmatched
            - **<50%**: Poor - Many students unmatched
            
            **Suggestions if low:**
            - Increase topic capacities
            - Increase supervisor capacities
            - Add more topics
            - Review student preferences (may be too restrictive)
            """)
    
    with col3:
        student_sat = report['student_satisfaction']
        if student_sat['average_rank']:
            avg_rank = student_sat['average_rank']
            st.metric(
                "Avg Student Rank",
                f"{avg_rank:.2f}",
                "Lower is better"
            )
            with st.expander("ℹ️ What is Student Satisfaction?"):
                st.markdown(f"""
                **Student Satisfaction** measures how well students' preferences were met.
                
                **Current Result:** Average rank of {avg_rank:.2f}
                - Rank 1 = Got their first choice
                - Rank 2 = Got their second choice
                - Higher ranks = Less preferred options
                
                **Interpretation:**
                - **1.0-1.5**: Excellent - Most students got top choices
                - **1.5-2.5**: Good - Students generally satisfied
                - **2.5-3.5**: Fair - Some students got lower preferences
                - **>3.5**: Poor - Many students got low preferences
                
                **Suggestions if high:**
                - Students may need to provide more diverse preferences
                - Consider adding more topics in popular areas
                - Review if preferences are too concentrated
                """)
        else:
            st.metric("Avg Student Rank", "N/A", "No matches")
    
    with col4:
        constraints = report['constraint_satisfaction']
        status = "✅ Satisfied" if constraints['all_constraints_satisfied'] else "❌ Violations"
        st.metric(
            "Constraints",
            status,
            f"{constraints['violation_count']} violations"
        )
        with st.expander("ℹ️ What are Constraints?"):
            st.markdown("""
            **Constraints** ensure capacity limits are respected.
            
            - **Topics**: No capacity limit (only supervisor capacity matters)
            - **Supervisor Capacity**: Maximum total students per supervisor
            
            **Interpretation:**
            - ✅ **Satisfied**: All capacity limits respected
            - ❌ **Violations**: Some limits exceeded (algorithm error)
            
            **If violations exist:**
            - This indicates a bug in the algorithm
            - Check input data for errors
            - Verify capacity values are correct
            """)
    
    # Round Statistics
    if 'round_stats' in st.session_state and st.session_state['round_stats']['total_rounds'] > 0:
        st.markdown("---")
        st.subheader("🔄 Matching Rounds")
        round_stats = st.session_state['round_stats']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rounds", round_stats['total_rounds'])
        with col2:
            st.metric("Matched Students", round_stats['matched_count'])
        with col3:
            st.metric("Unmatched Students", round_stats['unmatched_count'])
        
        # Round breakdown
        st.markdown("#### Round-by-Round Breakdown")
        round_data = []
        for round_num in sorted(round_stats['round_counts'].keys()):
            count = round_stats['round_counts'][round_num]
            round_data.append({
                'Round': round_num,
                'Students Matched': count,
                'Cumulative': sum(round_stats['round_counts'][r] for r in range(1, round_num + 1))
            })
        
        if round_data:
            round_df = pd.DataFrame(round_data)
            st.dataframe(round_df, use_container_width=True, hide_index=True)
        
        with st.expander("ℹ️ About Matching Rounds"):
            st.markdown("""
            **Sequential Round Matching:**
            
            The algorithm runs in multiple rounds to maximize matches:
            
            1. **Round 1**: All students apply to their most preferred topic
            2. **Round 2+**: Unmatched students continue with their remaining preferences
            3. **Stopping**: Algorithm stops when all students are matched or no new matches occur
            
            **Benefits:**
            - Maximizes total number of matches
            - Gives students multiple opportunities to be matched
            - Handles capacity constraints more effectively
            
            **Interpretation:**
            - **1 Round**: All students matched in first attempt (ideal)
            - **2-3 Rounds**: Normal - some students needed second/third preferences
            - **4+ Rounds**: May indicate capacity constraints or preference mismatches
            """)
    
    # Improvement Suggestions
    st.markdown("---")
    st.subheader("💡 Improvement Suggestions")
    
    suggestions = []
    
    # Check stability
    if not report['stability']['is_stable']:
        suggestions.append({
            'type': 'warning',
            'title': 'Stability Issues Detected',
            'message': f"The matching has {report['stability']['blocking_pairs']} blocking pairs. Consider:",
            'actions': [
                'Review student preferences - may be too concentrated',
                'Check if topic capacities are appropriate',
                'Verify supervisor capacities are sufficient',
                'Consider adding more topics in popular areas'
            ]
        })
    
    # Check match rate with detailed diagnostics
    if report['efficiency']['student_match_rate'] < 0.9:
        unmatched = report['efficiency']['total_students'] - report['efficiency']['matched_students']
        
        # Calculate capacity gaps (topics have no capacity limit)
        total_supervisor_capacity = sum(s.capacity for s in supervisors.values())
        capacity_gap = len(students) - total_supervisor_capacity
        sup_capacity_gap = 0  # Not applicable - topics have no capacity
        
        # Analyze unmatched students' preferences
        unmatched_students = [r for r in results if r['ProjectID'] is None]
        unmatched_prefs = {}
        for r in unmatched_students:
            student_id = r['StudentID']
            student = students[student_id]
            for pref in student.preferences:
                unmatched_prefs[pref] = unmatched_prefs.get(pref, 0) + 1
        
        # Build detailed recommendations
        detailed_actions = []
        
        if capacity_gap > 0:
            needed_per_sup = int(capacity_gap / len(supervisors)) + 1
            detailed_actions.append(f'**HIGH PRIORITY:** Increase supervisor capacities by {needed_per_sup} students each (need {capacity_gap} more slots total)')
        
        # Note: Topics have no capacity limit, so no topic capacity gap
            needed_per_sup = int(sup_capacity_gap / len(supervisors)) + 1
            detailed_actions.append(f'**HIGH PRIORITY:** Increase supervisor capacities by {needed_per_sup} students each (need {sup_capacity_gap} more slots)')
        
        if unmatched_prefs:
            top_unmatched = sorted(unmatched_prefs.items(), key=lambda x: x[1], reverse=True)[:3]
            detailed_actions.append(f'**MEDIUM PRIORITY:** Increase capacity for popular unmatched topics: {", ".join([f"{t} ({c} requests)" for t, c in top_unmatched])}')
        
        # Check supervisor coverage
        supervisor_coverage = {}
        for bachelor in ['BDBA', 'BCSAI', 'BBA+BDBA']:
            for topic_id in projects.keys():
                covered = any((bachelor, topic_id) in sup.bachelor_topic_expertise 
                             for sup in supervisors.values())
                if bachelor not in supervisor_coverage:
                    supervisor_coverage[bachelor] = {'total': 0, 'covered': 0}
                supervisor_coverage[bachelor]['total'] += 1
                if covered:
                    supervisor_coverage[bachelor]['covered'] += 1
        
        for bachelor, coverage in supervisor_coverage.items():
            coverage_pct = (coverage['covered'] / coverage['total'] * 100) if coverage['total'] > 0 else 0
            if coverage_pct < 60:
                detailed_actions.append(f'**MEDIUM PRIORITY:** Improve supervisor coverage for {bachelor} students (only {coverage_pct:.1f}% of topics covered)')
        
        if len(projects) < len(students) * 0.25:
            detailed_actions.append(f'**LOW PRIORITY:** Consider adding more topics (currently {len(projects)} topics for {len(students)} students)')
        
        suggestions.append({
            'type': 'warning',
            'title': f'Low Match Rate: {unmatched} Students Unmatched ({report["efficiency"]["student_match_rate"]*100:.1f}% matched)',
            'message': f"**Capacity Analysis:**\n- Topics: {len(projects)} (no capacity limit)\n- Supervisor capacity: {total_supervisor_capacity} students\n- Students: {len(students)}",
            'actions': detailed_actions if detailed_actions else [
                'All constraints appear satisfied. Low match rate may be due to preference misalignment.',
                'Review unmatched students\' preferences - they may be too restrictive',
                'Consider if some topics are oversubscribed while others are underutilized'
            ]
        })
    
    # Check student satisfaction
    if report['student_satisfaction']['average_rank'] and report['student_satisfaction']['average_rank'] > 2.5:
        suggestions.append({
            'type': 'info',
            'title': 'Student Satisfaction Could Be Improved',
            'message': f"Average student rank is {report['student_satisfaction']['average_rank']:.2f}. To improve:",
            'actions': [
                'Encourage students to provide more diverse preferences',
                'Add more topics in popular areas',
                'Review if preferences are too concentrated on few topics',
                'Review supervisor capacity - topics have no capacity limit'
            ]
        })
    
    # Check fairness
    if report['fairness']['gini_coefficient'] and report['fairness']['gini_coefficient'] > 0.3:
        suggestions.append({
            'type': 'info',
            'title': 'Fairness Concerns',
            'message': f"Gini coefficient of {report['fairness']['gini_coefficient']:.3f} indicates uneven satisfaction distribution. Consider:",
            'actions': [
                'Review if some students consistently get better matches',
                'Check if preferences are balanced across topics',
                'Consider implementing fairness constraints',
                'Review supervisor preference rankings'
            ]
        })
    
    # Check project utilization
    if report['efficiency']['project_utilization'] < 0.7:
        suggestions.append({
            'type': 'info',
            'title': 'Low Topic Utilization',
            'message': f"Only {report['efficiency']['project_utilization']*100:.1f}% of topics are filled. Suggestions:",
            'actions': [
                'Review if some topics are unpopular',
                'Consider reducing capacity of underutilized topics',
                'Check if topic descriptions need improvement',
                'Consider consolidating similar topics'
            ]
        })
    
    if suggestions:
        for suggestion in suggestions:
            if suggestion['type'] == 'warning':
                st.warning(f"**{suggestion['title']}**\n\n{suggestion['message']}\n\n" + 
                          "\n".join([f"• {action}" for action in suggestion['actions']]))
            else:
                st.info(f"**{suggestion['title']}**\n\n{suggestion['message']}\n\n" + 
                       "\n".join([f"• {action}" for action in suggestion['actions']]))
    else:
        st.success("✅ **Excellent Matching!** All metrics look good. No major improvements needed.")
    
    st.markdown("---")
    
    # Unmatched Students Analysis
    unmatched_results = [r for r in results if r['ProjectID'] is None]
    if unmatched_results:
        st.subheader(f"❌ Unmatched Students ({len(unmatched_results)})")
        
        st.markdown("""
        The following students could not be matched to any of their preferred topics.
        Below are the reasons why each student couldn't be matched:
        """)
        
        # Analyze reasons for each unmatched student
        unmatched_analysis = []
        
        for r in unmatched_results:
            student_id = r['StudentID']
            student = students[student_id]
            student_bachelor = algorithm._get_student_bachelor(student_id)
            
            reasons = []
            
            # Check each preference
            for pref_idx, topic_id in enumerate(student.preferences, 1):
                topic = projects.get(topic_id)
                if not topic:
                    reasons.append(f"Preference {pref_idx} ({topic_id}): Topic doesn't exist")
                    continue
                
                # Check if supervisor exists for this bachelor-topic combination
                supervisor_id = algorithm.topic_supervisors.get((topic_id, student_bachelor))
                
                if not supervisor_id:
                    reasons.append(f"Preference {pref_idx} ({topic_id}): No supervisor available for {student_bachelor} students")
                else:
                    supervisor = supervisors[supervisor_id]
                    
                    # Check if supervisor is at capacity
                    assigned_to_supervisor = []
                    for other_student_id, assigned_topic_id in algorithm.student_assignments.items():
                        if assigned_topic_id:
                            other_bachelor = algorithm._get_student_bachelor(other_student_id)
                            other_supervisor = algorithm.topic_supervisors.get((assigned_topic_id, other_bachelor))
                            if other_supervisor == supervisor_id:
                                assigned_to_supervisor.append(other_student_id)
                    
                    if len(assigned_to_supervisor) >= supervisor.capacity:
                        reasons.append(f"Preference {pref_idx} ({topic_id}): Supervisor {supervisor_id} at capacity ({len(assigned_to_supervisor)}/{supervisor.capacity})")
                    else:
                        # Supervisor has capacity but student still not matched - likely timing/order issue
                        reasons.append(f"Preference {pref_idx} ({topic_id}): Already allocated to other students before this student could apply")
            
            # Compile summary
            primary_reason = "All preferences were unavailable"
            no_supervisor_count = sum(1 for r in reasons if "No supervisor available" in r)
            at_capacity_count = sum(1 for r in reasons if "at capacity" in r)
            
            if no_supervisor_count == len(student.preferences):
                primary_reason = f"No supervisors available for {student_bachelor} students in any preferred topic"
            elif at_capacity_count > 0:
                primary_reason = f"All preferred supervisors at capacity ({at_capacity_count}/{len(student.preferences)} topics)"
            
            unmatched_analysis.append({
                'Student': student_id,
                'Program': student_bachelor,
                'Preferences': ', '.join(student.preferences),
                'Primary Reason': primary_reason,
                'Details': ' | '.join(reasons[:3])  # Show first 3 preferences
            })
        
        # Display as table
        unmatched_df = pd.DataFrame(unmatched_analysis)
        st.dataframe(unmatched_df, use_container_width=True, hide_index=True)
        
        # Summary of reasons
        st.markdown("#### 📊 Summary of Unmatched Reasons")
        reason_counts = {}
        for analysis in unmatched_analysis:
            reason = analysis['Primary Reason']
            if 'No supervisors available' in reason:
                key = 'No supervisor coverage for bachelor-topic combination'
            elif 'at capacity' in reason:
                key = 'All preferred supervisors at capacity'
            else:
                key = 'Topics already allocated'
            reason_counts[key] = reason_counts.get(key, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        for i, (reason, count) in enumerate(reason_counts.items()):
            with [col1, col2, col3][i % 3]:
                st.metric(reason, count)
        
        # Recommendations
        st.markdown("#### 💡 Recommendations to Match These Students")
        recommendations = []
        
        if 'No supervisor coverage for bachelor-topic combination' in reason_counts:
            recommendations.append("• **Add supervisors** who can supervise the unmatched bachelor-topic combinations")
        
        if 'All preferred supervisors at capacity' in reason_counts:
            recommendations.append("• **Increase supervisor capacities** or add more supervisors for popular topics")
            recommendations.append("• **Encourage students** to diversify their preferences to less popular topics")
        
        if 'Topics already allocated' in reason_counts:
            recommendations.append("• **Run additional rounds** to give students more chances to match")
            recommendations.append("• **Review matching order** - some students may need priority")
        
        for rec in recommendations:
            st.markdown(rec)
    else:
        st.success("✅ **All students matched!** No unmatched students to report.")
    
    st.markdown("---")
    
    # Detailed Results Table with explanations
    st.subheader("📋 Detailed Matching Results")
    
    with st.expander("ℹ️ Understanding the Results Table"):
        st.markdown("""
        **Column Explanations:**
        
        - **StudentID**: Unique identifier for each student
        - **ProjectID/TopicID**: The topic assigned to the student (None if unmatched)
        - **Area**: Academic area of the topic (Data Science, Machine Learning, etc.)
        - **SupervisorID**: The supervisor assigned to supervise this topic
        - **ExpertiseLevel**: Supervisor's expertise level for this specific topic (Expert, Advanced, Intermediate, Beginner)
        - **StudentRank**: Position of assigned topic in student's preference list (1 = first choice, 2 = second choice, etc.)
        - **MatchingRound**: The round in which the student was matched (1, 2, 3, etc.)
        
        **How to Read:**
        - Lower StudentRank = Better match (closer to student's preference)
        - Rank 1 = Got their top preference
        - Rank 5 = Got their 5th choice
        """)
    
    results_df = pd.DataFrame(results)
    
    # Add program column for better visualization
    if 'StudentID' in results_df.columns:
        def get_program(sid):
            if sid.startswith('BDBA') and not sid.startswith('BBA_BDBA'):
                return 'BDBA'
            elif sid.startswith('BCSAI'):
                return 'BCSAI'
            elif sid.startswith('BBA_BDBA'):
                return 'BBA+BDBA'
            elif sid.startswith('BBA') and not sid.startswith('BBA_'):
                return 'BBA'
            else:
                return 'Other'
        
        results_df['Program'] = results_df['StudentID'].apply(get_program)
        
        # Reorder columns
        column_order = ['StudentID', 'Program', 'ProjectID', 'Area', 'SupervisorID', 'ExpertiseLevel', 'StudentRank', 'MatchingRound']
        results_df = results_df[[col for col in column_order if col in results_df.columns]]
    
    st.dataframe(results_df, use_container_width=True, hide_index=True)
    
    # Summary statistics by program
    if 'Program' in results_df.columns:
        st.markdown("#### 📊 Summary by Program")
        program_stats = []
        for program in results_df['Program'].unique():
            program_df = results_df[results_df['Program'] == program]
            matched = program_df['ProjectID'].notna().sum()
            total = len(program_df)
            avg_rank = program_df['StudentRank'].mean() if matched > 0 else None
            
            program_stats.append({
                'Program': program,
                'Total Students': total,
                'Matched': matched,
                'Match Rate': f"{matched/total*100:.1f}%",
                'Avg Student Rank': f"{avg_rank:.2f}" if avg_rank else "N/A"
            })
        
        stats_df = pd.DataFrame(program_stats)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Visualizations with explanations
    st.markdown("---")
    st.subheader("📊 Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Satisfaction Distribution")
        with st.expander("ℹ️ How to Read This Chart"):
            st.markdown("""
            This chart shows how satisfied students and supervisors are with the matching.
            
            **Left Chart (Student Satisfaction):**
            - X-axis: Rank of assigned topic (1 = first choice, 2 = second choice, etc.)
            - Y-axis: Number of students
            - Lower ranks (left side) = Better satisfaction
            - Red dashed line = Average rank
            
            **Right Chart (Program Distribution):**
            - Shows distribution of matched students by bachelor program
            - BDBA, BCSAI, and BBA+BDBA programs
            - Helps verify balanced matching across programs
            
            **Interpretation:**
            - Most bars on the left = Good satisfaction
            - Even distribution = Fair matching
            - Most bars on the right = Lower satisfaction
            """)
        fig1 = plot_satisfaction_distribution(results)
        st.pyplot(fig1)
        plt.close()
    
    with col2:
        st.markdown("#### Matching Summary Dashboard")
        with st.expander("ℹ️ How to Read This Dashboard"):
            st.markdown("""
            This dashboard provides a quick overview of matching quality.
            
            **Top Left - Stability:**
            - Green = Stable matching (optimal)
            - Red = Unstable (improvements possible)
            
            **Top Right - Efficiency:**
            - Shows percentage of students matched and topics filled
            - Higher = Better utilization
            
            **Bottom Left - Student Satisfaction:**
            - Average and median ranks
            - Lower = Better (closer to preferences)
            
            **Bottom Right - Constraints:**
            - Green = All capacity limits respected
            - Red = Some violations (algorithm error)
            """)
        fig2 = plot_matching_summary(report)
        st.pyplot(fig2)
        plt.close()
    
    # Detailed Metrics with explanations
    st.markdown("---")
    st.subheader("📊 Detailed Evaluation Metrics")
    
    tabs = st.tabs(["Stability", "Satisfaction", "Efficiency", "Fairness", "Constraints"])
    
    with tabs[0]:
        st.markdown("### Stability Analysis")
        st.markdown("""
        **What is Stability?**
        
        A stable matching ensures that no student-topic pair would both prefer each other over their current assignments. 
        This is a fundamental property of good matching algorithms.
        """)
        
        stability = report['stability']
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Is Stable", "Yes" if stability['is_stable'] else "No")
            st.metric("Blocking Pairs", stability['blocking_pairs'])
        
        with col2:
            st.metric("Stability Score", f"{stability['stability_score']:.3f}", 
                     help="1.0 = Perfectly stable, 0.0 = Many blocking pairs")
        
        st.json(stability)
        
        if not stability['is_stable']:
            st.warning("""
            **Unstable Matching Detected**
            
            This matching has blocking pairs, meaning some students and topics would prefer each other 
            over their current assignments. While the algorithm tries to minimize this, it may occur 
            due to capacity constraints or preference conflicts.
            """)
    
    with tabs[1]:
        st.markdown("### Satisfaction Analysis")
        st.markdown("""
        **Satisfaction Metrics** measure how well the matching aligns with student preferences. 
        Lower ranks indicate better satisfaction (1 = got first choice).
        """)
        
        st.markdown("#### Student Satisfaction")
        student_sat = report['student_satisfaction']
        
        if student_sat['average_rank']:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Rank", f"{student_sat['average_rank']:.2f}")
                st.metric("Median Rank", f"{student_sat['median_rank']:.2f}")
            with col2:
                st.metric("Best Rank", student_sat['min_rank'])
                st.metric("Worst Rank", student_sat['max_rank'])
            with col3:
                st.metric("Standard Deviation", f"{student_sat['std_rank']:.2f}")
                st.metric("Matched Students", f"{student_sat['students_matched']}/{student_sat['students_matched'] + student_sat['students_unmatched']}")
            
            with st.expander("📊 View Raw Data"):
                st.json(student_sat)
        else:
            st.info("No students matched yet.")
    
    with tabs[2]:
        st.markdown("### Efficiency Analysis")
        st.markdown("""
        **Efficiency Metrics** measure how well resources (topics, supervisors) are utilized 
        and how many students were successfully matched.
        """)
        
        efficiency = report['efficiency']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Student Match Rate", f"{efficiency['student_match_rate']*100:.1f}%")
        with col2:
            st.metric("Project Utilization", f"{efficiency['project_utilization']*100:.1f}%")
        with col3:
            st.metric("Matched Students", f"{efficiency['matched_students']}/{efficiency['total_students']}")
        with col4:
            st.metric("Filled Topics", f"{efficiency['filled_projects']}/{efficiency['total_projects']}")
        
        st.json(efficiency)
        
        if efficiency['student_match_rate'] < 1.0:
            unmatched = efficiency['total_students'] - efficiency['matched_students']
            st.info(f"""
            **{unmatched} students were not matched.**
            
            This could be due to:
            - Insufficient supervisor capacity for preferred topics
            - No supervisors available for student's bachelor program in preferred topics
            - All supervisors at capacity for student's top preferences
            - Limited topic coverage for specific bachelor programs
            
            💡 See the "Unmatched Students Analysis" section above for detailed reasons.
            """)
    
    with tabs[3]:
        st.markdown("### Fairness Analysis")
        st.markdown("""
        **Fairness Metrics** measure how evenly satisfaction is distributed across all students. 
        A fair matching ensures no group is systematically disadvantaged.
        """)
        
        fairness = report['fairness']
        
        if fairness['gini_coefficient'] is not None:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Gini Coefficient", f"{fairness['gini_coefficient']:.3f}",
                         help="0 = Perfect equality, 1 = Maximum inequality")
            
            with col2:
                st.metric("Variance", f"{fairness['variance']:.3f}",
                         help="Lower variance = More consistent satisfaction")
            
            with col3:
                if fairness['coefficient_of_variation']:
                    st.metric("Coefficient of Variation", f"{fairness['coefficient_of_variation']:.3f}",
                             help="Relative variability in satisfaction")
            
            st.json(fairness)
            
            # Interpretation
            gini = fairness['gini_coefficient']
            if gini < 0.2:
                st.success("**Excellent Fairness**: Satisfaction is very evenly distributed.")
            elif gini < 0.3:
                st.info("**Good Fairness**: Satisfaction is reasonably distributed.")
            elif gini < 0.4:
                st.warning("**Moderate Fairness**: Some inequality in satisfaction distribution.")
            else:
                st.error("**Poor Fairness**: Significant inequality in satisfaction. Consider reviewing preferences and capacities.")
        else:
            st.info("Fairness metrics cannot be calculated (no matches or insufficient data).")
    
    with tabs[4]:
        st.markdown("### Constraint Satisfaction")
        st.markdown("""
        **Constraint Satisfaction** verifies that all capacity limits are respected:
        - Topic capacities (max students per topic)
        - Supervisor capacities (max total students per supervisor)
        """)
        
        constraints = report['constraint_satisfaction']
        
        col1, col2 = st.columns(2)
        
        with col1:
            status = "✅ All Satisfied" if constraints['all_constraints_satisfied'] else "❌ Violations Found"
            st.metric("Status", status)
        
        with col2:
            st.metric("Violation Count", constraints['violation_count'])
        
        st.json(constraints)
        
        if constraints['violations']:
            st.error("**⚠️ Constraint Violations Detected!**")
            st.write("The following violations were found:")
            for violation in constraints['violations']:
                st.write(f"- {violation}")
            st.warning("""
            **Important**: Constraint violations indicate an algorithm error. 
            This should not occur in a properly functioning matching algorithm.
            Please check your input data and report this issue.
            """)
        else:
            st.success("✅ **All constraints satisfied!** All capacity limits are respected.")


def show_about_page():
    """Display about page."""
    st.header("ℹ️ About")
    
    st.markdown("""
    ### Student-Topic Allocation Matching Algorithm
    
    This application implements the **SPA-student algorithm** for allocating students to capstone topics.
    
    **Supported Programs:**
    - **BDBA**: Bachelor in Data and Business Analytics
    - **BCSAI**: Bachelor in Computer Science and Artificial Intelligence  
    - **BBA+BDBA**: Joint Bachelor in Business Administration + Data and Business Analytics
    
    #### Algorithm Reference
    
    **Abraham, D.J., Irving, R.W., and Manlove, D.M. (2007)**  
    Two algorithms for the student-project allocation problem.  
    _Journal of Discrete Algorithms_, 5(1), pp. 73-90.  
    doi:10.1016/j.jda.2006.03.006
    
    #### Implementation Reference
    
    Based on the implementation at:  
    https://richarddmorey.github.io/studentProjectAllocation/
    
    #### Features
    
    - ✅ **Stable Matching**: Ensures no blocking pairs exist
    - ✅ **Capacity Constraints**: Respects project and supervisor limits
    - ✅ **Preference-Based**: Considers both student and supervisor preferences
    - ✅ **Comprehensive Evaluation**: Multiple metrics and visualizations
    
    #### Input Format
    
    **Students File:**
    ```
    StudentID: Topic1, Topic2, Topic3, ...
    ```
    
    **Topics File:**
    ```
    TopicID: Area, [Student1, Student2, ...]
    ```
    
    **Areas:** Data Science, Machine Learning, Computer Science, Mathematics, etc.
    
    **Supervisors File:**
    ```
    SupervisorID: MaximumCapacity (max 10), Bachelor1:Topic1:ExpertiseLevel1, Bachelor1:Topic2:ExpertiseLevel2, Bachelor2:Topic1:ExpertiseLevel1, ...
    ```
    
    **Constraints:**
    - Maximum capacity: 10 students per supervisor
    - Maximum bachelor-topic combinations: 5 per supervisor
    
    **Format:** Each combination specifies: BachelorProgram:TopicID:ExpertiseLevel
    
    **Expertise Levels:** Expert, Advanced, Intermediate, Beginner
    
    **Supervisors File:**
    ```
    SupervisorID: MaximumCapacity, Student1, Student2, Student3, ...
    ```
    
    **Note:** Supervisor MaximumCapacity is the total number of students a supervisor can handle across all topics.
    
    #### Evaluation Metrics
    
    - **Stability**: Checks for blocking pairs
    - **Student Satisfaction**: Average rank of assigned projects
    - **Efficiency**: Match rates and utilization
    - **Fairness**: Distribution of satisfaction (Gini coefficient)
    - **Constraint Satisfaction**: Verification of capacity limits
    """)


if __name__ == "__main__":
    main()

