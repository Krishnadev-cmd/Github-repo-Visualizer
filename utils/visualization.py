import plotly.graph_objects as go
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any

class BranchVisualizer:
    def __init__(self):
        # Define color schemes
        self.branch_colors = {
            'main': '#2ECC71',      # Green
            'master': '#2ECC71',    # Green
            'develop': '#3498DB',   # Blue
            'release': '#E74C3C',   # Red
            'feature': '#9B59B6',   # Purple
            'hotfix': '#E67E22',    # Orange
            'bugfix': '#F1C40F'     # Yellow
        }
        
        self.default_colors = [
            '#1ABC9C', '#16A085', '#27AE60', '#2980B9', '#8E44AD', 
            '#2C3E50', '#F39C12', '#D35400', '#C0392B', '#BDC3C7'
        ]
        
    def assign_branch_colors(self, branch_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Assign colors to branches based on their names
        """
        branch_to_color = {}
        used_colors = 0
        
        for branch in branch_data:
            branch_name = branch['name']
            color_assigned = False
            
            # Check if branch name contains any predefined type
            for branch_type, color in self.branch_colors.items():
                if branch_type in branch_name.lower():
                    branch_to_color[branch_name] = color
                    color_assigned = True
                    break
            
            # Assign default color if no predefined type matches
            if not color_assigned:
                branch_to_color[branch_name] = self.default_colors[used_colors % len(self.default_colors)]
                used_colors += 1
                
        return branch_to_color

    def process_commit_data(self, 
                          commits_data: List[Dict[str, Any]], 
                          branch_data: List[Dict[str, Any]]) -> Tuple[Dict[str, List[str]], Dict[str, datetime], Dict[str, List[str]]]:
        """
        Process commit data to determine branch relationships and commit dates
        """
        # Create mappings
        commit_to_branch = defaultdict(list)
        branch_tips = {branch['name']: branch['commit'] for branch in branch_data}
        
        # Create commit parent and date mappings
        commit_parents = {
            commit['sha']: commit['parents'] 
            for commit in commits_data
        }
        
        commit_dates = {
            commit['sha']: datetime.strptime(commit['date'], '%Y-%m-%d %H:%M:%S') 
            for commit in commits_data
        }
        
        # Assign commits to branches
        for branch_name, tip_commit in branch_tips.items():
            current_commit = tip_commit
            while current_commit in commit_parents:
                commit_to_branch[current_commit].append(branch_name)
                if not commit_parents[current_commit]:
                    break
                current_commit = commit_parents[current_commit][0]
                
        return commit_to_branch, commit_dates, commit_parents

    def prepare_visualization_data(self,
                                 commits_data: List[Dict[str, Any]],
                                 commit_to_branch: Dict[str, List[str]],
                                 commit_dates: Dict[str, datetime],
                                 commit_parents: Dict[str, List[str]],
                                 branch_to_color: Dict[str, str],
                                 branch_lanes: Dict[str, int]) -> Tuple[List, List, List, List, List[go.Scatter]]:
        """
        Prepare data for visualization including dots and lines
        """
        dots_x, dots_y, dots_color, dots_text = [], [], [], []
        branch_traces = []
        
        # Process commits and create branch traces
        for branch_name, lane in branch_lanes.items():
            branch_color = branch_to_color[branch_name]
            branch_commits = sorted(
                [(sha, commit_dates[sha]) for sha, branches in commit_to_branch.items() if branch_name in branches],
                key=lambda x: x[1]
            )
            
            if branch_commits:
                # Create branch line trace
                x_data = [date for _, date in branch_commits]
                y_data = [lane] * len(branch_commits)
                
                branch_traces.append(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines',
                    line=dict(color=branch_color, width=2),
                    name=branch_name,
                    showlegend=True,
                    hoverinfo='none'
                ))

        # Process commits for dots
        for commit in commits_data:
            commit_sha = commit['sha']
            commit_date = commit_dates[commit_sha]
            
            # Handle branches for this commit
            branches = commit_to_branch[commit_sha]
            if not branches:
                branches = ['(detached)']
                color = '#95A5A6'  # Gray for detached commits
            else:
                color = branch_to_color[branches[0]]
            
            # Add commit dots
            for branch in branches:
                lane = branch_lanes.get(branch, len(branch_lanes))
                dots_x.append(commit_date)
                dots_y.append(lane)
                dots_color.append(color)
                dots_text.append(
                    f"Commit: {commit_sha[:7]}<br>"
                    f"Branch: {', '.join(branches)}<br>"
                    f"Author: {commit['author']}<br>"
                    f"Date: {commit_date}<br>"
                    f"Message: {commit['message'][:50]}..."
                )
                        
        return dots_x, dots_y, dots_color, dots_text, branch_traces

    def create_plotly_figure(self,
                           dots_x: List[datetime],
                           dots_y: List[int],
                           dots_color: List[str],
                           dots_text: List[str],
                           branch_traces: List[go.Scatter],
                           branch_lanes: Dict[str, int]) -> go.Figure:
        """
        Create and configure the Plotly figure
        """
        fig = go.Figure()

        # Add branch lines
        for trace in branch_traces:
            fig.add_trace(trace)

        # Add commit dots
        fig.add_trace(go.Scatter(
            x=dots_x,
            y=dots_y,
            mode='markers',
            marker=dict(
                size=12,
                color=dots_color,
                line=dict(width=2, color='white')
            ),
            text=dots_text,
            hoverinfo='text',
            showlegend=False
        ))

        # Configure layout
        fig.update_layout(
            showlegend=True,
            plot_bgcolor='#282b30',
            paper_bgcolor='#282b30',
            margin=dict(l=50, r=50, t=30, b=50),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)',
                title='Commit Timeline',
                title_font_color='white',
                tickfont_color='white'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)',
                ticktext=list(branch_lanes.keys()),
                tickvals=list(branch_lanes.values()),
                title='Branches',
                title_font_color='white',
                tickfont_color='white'
            ),
            hoverlabel=dict(
                bgcolor='white',
                font_size=12
            ),
            legend=dict(
                font=dict(color='white')
            )
        )
        
        return fig
