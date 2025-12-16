class KeyBuilder:
    @staticmethod
    def messages(key: str):
        return f"messages:{key}"

    @staticmethod
    def summary(key: str):
        return f"summary:{key}"

    @staticmethod
    def chat_status(chat_id: str, topic_id: str):
        return f"group:status:{chat_id}:{topic_id}"

    @staticmethod
    def user_obj(user_id: int) -> str:
        return f"user:{user_id}"

    @staticmethod
    def group_obj(group_id: int, topic_id: int) -> str:
        return f"group:{group_id}:{topic_id}"

    @staticmethod
    def answers_obj(group_id: int, topic_id: int, message_id: int) -> str:
        return f"answers:{group_id}:{topic_id}:{message_id}"
