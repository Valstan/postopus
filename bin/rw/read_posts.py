import time

import requests

from env_loader import session


def read_posts(group_dict, count):
    """
    Читает посты из групп VK используя стандартный метод wall.get.

    Args:
        group_dict: словарь {имя_региона: group_id}
        count: количество постов для получения из каждой группы

    Returns:
        list постов
    """
    get_posts = []
    group_list = list(group_dict.items())  # [(name, group_id), ...]

    for group_name, group_id in group_list:
        for i in range(3):  # retry logic
            try:
                # Используем стандартный метод wall.get вместо execute.wallGet
                response = requests.post(
                    "https://api.vk.com/method/wall.get",
                    params={
                        "owner_id": group_id,
                        "count": count,
                        "access_token": session["token"],
                        "v": "5.131",
                    },
                )
                data = response.json()

                if "error" in data:
                    print(f"⚠️  Ошибка VK API для группы {group_name} ({group_id}): {data['error'].get('error_msg', 'Unknown error')}")
                    break

                if "response" in data and "items" in data["response"]:
                    items = data["response"]["items"]
                    # Добавляем информацию о группе к каждому посту
                    for item in items:
                        item["_source_group_name"] = group_name
                        item["_source_group_id"] = group_id
                    get_posts.extend(items)
                break
            except Exception as e:
                print(f"⚠️  Ошибка запроса для группы {group_name}: {e}")
                time.sleep(1)

        time.sleep(0.5)  # небольшой delay между запросами к разным группам

    return get_posts


if __name__ == "__main__":
    pass
