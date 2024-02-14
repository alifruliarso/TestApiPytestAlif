from dataclasses import dataclass

@dataclass
class Task():
    is_done: bool
    content: str
    user_id: str
    task_id: str
    ttl: float
    created_time: float
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            is_done = data.get("is_done"),
            content = data.get("content"),
            user_id = data.get("user_id"),
            task_id = data.get("task_id"),
            ttl = data.get("ttl"),
            created_time = data.get("created_time"),
        )
