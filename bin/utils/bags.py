from config import session


def bags(sample_text='', string='', url=''):
    if session['bags'] == "0":
        pass
    elif session['bags'] == "1":
        print(f"\n!!! Слишком старый !!!\n{sample_text}\n{url}")
    elif session['bags'] == "2":
        print(f"\n!!! Уже публиковался (по тексту) !!!\n{sample_text}\n{url}")
    elif bags == "3":
        print(f"____!!! Строка в черном списке !!!______\n"
              f"{string}\n"
              f"Не будет опубликован пост:\n"
              f"{sample_text}\n"
              f"{url}")
    elif session['bags'] == "4":
        print(f"\n!!! Есть атачментсы, но их мы удалим, потому что нет views !!!"
              f"\n{sample_text}"
              f"\n{url}")
    elif session['bags'] == "5":
        print(f"\n----- !!! Такая фотка уже была, пост не будет опубликован !!! -----"
              f"\n{sample_text}"
              f"\n{url}")
