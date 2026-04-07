"""Legacy utility: URL поста VK."""


def url_of_post(sample: dict) -> str:
    """Возвращает URL поста: https://vk.com/wall{owner_id}_{id}."""
    return f"https://vk.com/wall{sample['owner_id']}_{sample['id']}"
