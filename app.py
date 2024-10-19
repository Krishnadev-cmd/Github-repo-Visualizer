import streamlit as st
import pandas as pd

def create_sidebar():
    """Create and configure the sidebar"""
    with st.sidebar:
        st.header("Settings")
        
        # Repository URL input with example
        st.markdown("#### Repository URL")
        repo_url = st.text_input(
            "Enter the full GitHub repository URL",
            placeholder="https://github.com/owner/repo",
            help="Example: https://github.com/streamlit/streamlit"
        )
        
        # GitHub token input with explanation
        st.markdown("#### GitHub Token (Optional)")
        st.markdown("""
        A GitHub token increases API limits and allows access to private repositories.
        [Learn how to create a token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
        """)
        github_token = st.text_input(
            "Enter your GitHub token",
            type="password"
        )
        
        # Commit limit slider
        commit_limit = st.slider(
            "Number of commits to fetch", 
            min_value=10, 
            max_value=500, 
            value=100,
            help="Higher numbers may take longer to load"
        )
        
        analyze_button = st.button(
            "Analyze Repository",
            help="Click to start analyzing the repository"
        )
        
    return repo_url, github_token, commit_limit, analyze_button

def display_commit_history(commits_data):
    """Display commit history and statistics"""
    st.subheader("Commit History")
    
    if not commits_data:
        st.warning("No commit data available")
        return
        
    df_commits = pd.DataFrame(commits_data)
    st.dataframe(df_commits, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Commits Analyzed", len(commits_data))
    
    with col2:
        authors = df_commits['author'].value_counts()
        st.metric("Unique Contributors", len(authors))
    
    st.subheader("Author Contributions")
    st.bar_chart(authors)



if __name__ == "__main__":
    main()