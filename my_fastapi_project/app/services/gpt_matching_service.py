from openai import OpenAI
from sqlalchemy.orm import Session
from typing import List, Dict
from app.config import settings
from app.models import User, MatchingCategory

class GPTMatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_matching_candidates(self, user_id: int, category_id: int) -> List[Dict]:
        """GPT를 활용한 매칭 후보 찾기"""
        current_user = self.db.query(User).filter(User.id == user_id).first()
        category = self.db.query(MatchingCategory).filter(MatchingCategory.id == category_id).first()

        # 기본 쿼리 설정
        query = self.db.query(User).filter(User.id != user_id)
        
        # 팀원 매칭의 경우 같은 클래스로 제한
        if category.has_class_restriction:
            query = query.filter(User.class_id == current_user.class_id)

        candidates = query.all()

        # 각 후보에 대해 GPT 분석 수행
        matches = []
        for candidate in candidates:
            match_result = self._analyze_match(current_user, candidate, category.name)
            if match_result["score"] > 0.5:  # 매칭 점수가 50% 이상인 경우만 포함
                matches.append({
                    "user": candidate,
                    "score": match_result["score"],
                    "reasoning": match_result["reasoning"],
                    "recommendation": match_result["recommendation"]
                })

        # 매칭 점수로 정렬
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches[:10]  # 상위 10명만 반환

    def _analyze_match(self, user1: User, user2: User, category: str) -> Dict:
        """GPT를 사용하여 두 사용자 간의 매칭을 분석"""
        prompt = self._create_matching_prompt(user1, user2, category)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """
                    You are an expert matching system that analyzes compatibility between users.
                    Provide detailed analysis of their compatibility based on their profiles and the matching category.
                    Return your analysis in the following JSON format:
                    {
                        "score": <float between 0 and 1>,
                        "reasoning": "<detailed explanation of the matching>",
                        "recommendation": "<specific recommendation for their interaction>"
                    }
                    """},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # 응답 파싱
            result = eval(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"GPT API 호출 오류: {str(e)}")
            # 오류 발생 시 기본 값 반환
            return {
                "score": 0.0,
                "reasoning": "매칭 분석 중 오류가 발생했습니다.",
                "recommendation": "다시 시도해 주세요."
            }

    def _create_matching_prompt(self, user1: User, user2: User, category: str) -> str:
        """매칭 분석을 위한 프롬프트 생성"""
        return f"""
        Analyze the compatibility between these two users for {category} matching:

        User 1 Profile:
        - Major: {user1.major}
        - Programming Level: {user1.programmingLevel}/5
        - Programming Field: {user1.programmingField}
        - Programming Language: {user1.programmingLanguage}
        - MBTI: {user1.mbtiId}
        - Leadership Level: {user1.leadershipLevel}/5

        User 2 Profile:
        - Major: {user2.major}
        - Programming Level: {user2.programmingLevel}/5
        - Programming Field: {user2.programmingField}
        - Programming Language: {user2.programmingLanguage}
        - MBTI: {user2.mbtiId}
        - Leadership Level: {user2.leadershipLevel}/5

        Category Specific Considerations:
        {"- Must be in the same class" if category == "팀원 매칭" else ""}
        {"- Focus on programming compatibility and learning potential" if category == "스터디" else ""}
        {"- Consider team dynamics and project collaboration" if category == "팀원 매칭" else ""}

        Please analyze their compatibility and provide:
        1. A compatibility score (0-1)
        2. Detailed reasoning for the score
        3. Specific recommendations for their interaction

        Return the analysis in JSON format.
        """ 