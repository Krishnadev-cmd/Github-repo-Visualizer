import streamlit as st
import pandas as pd
from utils.validation import validate_github_url
from utils.visualization import create_branch_visualization
from utils.github_data import GitHubDataFetcher

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
def display_branch_info(branch_data):
    """Display branch information and statistics"""
    st.subheader("Branch Information")
    
    if not branch_data:
        st.warning("No branch data available")
        return
        
    df_branches = pd.DataFrame(branch_data)
    st.dataframe(df_branches, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Branches", len(branch_data))
    with col2:
        protected_branches = len([b for b in branch_data if b['protected']])
        st.metric("Protected Branches", protected_branches)

def main():
    st.title("Git Repository Visualizer")
    
    # Add a brief description
    st.markdown("""
    Analyze and visualize GitHub repository branches, commits, and contributions.
    Enter a repository URL in the sidebar to get started.
    """)
    
    repo_url, github_token, commit_limit, analyze_button = create_sidebar()

    if analyze_button:
        try:
            # Validate URL and get owner/repo
            owner, repo_name = validate_github_url(repo_url)
            
            # Initialize GitHub client and fetch data
            github_fetcher = GitHubDataFetcher(github_token)
            
            with st.spinner("Connecting to GitHub..."):
                repo = github_fetcher.get_repository(owner, repo_name)
            
            with st.spinner("Fetching repository data..."):
                commits_data = github_fetcher.get_commit_data(repo, commit_limit)
                branch_data = github_fetcher.get_branch_data(repo)
                
                # Show repository info
                st.success(f"Successfully connected to {owner}/{repo_name}")
                
                # Create tabs
                tab1, tab2, tab3 = st.tabs([
                    "Branch View", 
                    "Commit History", 
                    "Branch Information"
                ])
                
                with tab1:
                    st.subheader("Repository Branch Timeline")
                    if commits_data and branch_data:
                        fig = create_branch_visualization(commits_data, branch_data)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("No data available for visualization")
                
                with tab2:
                    display_commit_history(commits_data)
                
                with tab3:
                    display_branch_info(branch_data)

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.info("If the problem persists, please check your connection and try again later.")



if __name__ == "__main__":
    main()