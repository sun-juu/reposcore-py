#!/usr/bin/env python3

import requests
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict

class RepoAnalyzer:
    """Class to analyze repository participation for scoring"""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.participants: Dict = {}
        self.score_weights = {
            'PRs': 1,              #이 부분은 merge된 PR의 PR 갯수, issues 갯수만 세기 위해 임시로 1로 변경
            'issues_created': 1,   #향후 배점이 필요할 경우 PRs: 0.4, issues: 0.3으로 바꿔주세요.
        }
    
    def collect_PRs_and_issues(self) -> None:
        """
        collect_PRs와 collect_issues의 기능을 통합한 함수.
        GitHub 이슈 목록을 한 번에 가져온 뒤,
        pull_request 필드로 PR 여부를 구분하고,
        병합된 PR이면 PR 카운트로,
        일반 이슈라면 이슈 카운트로 기록한다.
        """
        page = 1
        per_page = 100

        merged_pr_count = 0
        issues_count = 0

        while True:
            url = f"https://api.github.com/repos/{self.repo_path}/issues?state=all&page={page}&per_page={per_page}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"⚠️ GitHub API 요청 실패: {response.status_code}")
                return

            items = response.json()
            if not items:
                break  # 더 이상 가져올 이슈(또는 PR)가 없으면 종료

            for item in items:
                author = item.get("user", {}).get("login", "Unknown")
                if author not in self.participants:
                    self.participants[author] = {
                        "PRs": 0,
                        "issues_created": 0,
                    }

                if "pull_request" in item:
                    merged_at = item.get("pull_request", {}).get("merged_at")
                    if merged_at is not None:
                        self.participants[author]["PRs"] += 1
                        merged_pr_count += 1
                else:
                    self.participants[author]["issues_created"] += 1
                    issues_count += 1
            page += 1

        print(f"병합된 PR 총 개수: {merged_pr_count}")
        print(f"issues 총 개수: {issues_count}")

    def calculate_scores(self) -> Dict:
        """Calculate participation scores for each contributor"""
        scores = {}
        for participant, activities in self.participants.items():
            total_score = (
                activities.get('PRs', 0) * self.score_weights['PRs'] +
                activities.get('issues_created', 0) * self.score_weights['issues_created']
            )
            scores[participant] = total_score

        # participants 딕셔너리 출력
        print("\n참여자별 활동 내역 (participants 딕셔너리):")
        for user, info in self.participants.items():
            print(f"{user}: {info}")

        return scores


    def generate_table(self, scores: Dict, save_path: str = "results") -> None:
        """Generate a table of participation scores"""
        df = pd.DataFrame.from_dict(scores, orient='index', columns=['Score'])
        df.to_csv(save_path)

    def generate_chart(self, scores: Dict, save_path: str = "results") -> None:
        """Generate a visualization of participation scores"""
        plt.figure(figsize=(10, 6))
        plt.bar(scores.keys(), scores.values())
        plt.xticks(rotation=45)
        plt.ylabel('Participation Score')
        plt.title('Repository Participation Scores')
        plt.tight_layout()
        plt.savefig(save_path)

