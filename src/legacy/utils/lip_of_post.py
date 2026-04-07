"""Legacy utility: уникальный ID поста VK."""


def lip_of_post(sample: dict) -> str:
    """Возвращает уникальный идентификатор поста: owner_id_id."""
    return f"{abs(sample['owner_id'])}_{sample['id']}"
