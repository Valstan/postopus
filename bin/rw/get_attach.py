def get_attach(msg, max_count=10):
    """
    Получает вложения из сообщения.
    Возвращает строку вложений и их количество.
    Фильтрует несовместимые типы вложений (audio+video).
    """
    if 'attachments' in msg:
        attach = ''
        count = 0
        has_audio = False
        has_video = False
        audio_attachments = []
        video_attachments = []
        other_attachments = []
        
        # Сначала собираем все вложения по типам
        for sample in msg['attachments']:
            type_attach = sample['type']
            
            if type_attach == 'link':
                continue
            elif type_attach == 'photos_list':
                other_attachments.append(('photos_list', sample[type_attach]))
                count += 10
            elif type_attach == 'audio':
                has_audio = True
                audio_attachments.append((type_attach, sample[type_attach]['owner_id'], '_', sample[type_attach]['id']))
                count += 1
            elif type_attach == 'video':
                has_video = True
                video_attachments.append((type_attach, sample[type_attach]['owner_id'], '_', sample[type_attach]['id']))
                count += 1
            else:
                other_attachments.append((type_attach, sample[type_attach]['owner_id'], '_', sample[type_attach]['id']))
                count += 1
        
        # Если есть и аудио и видео, оставляем только один тип (приоритет видео)
        if has_audio and has_video:
            # Оставляем видео, убираем аудио
            has_audio = False
            audio_attachments = []
            # Пересчитываем количество
            count = len(video_attachments) + len(other_attachments)
            for item in other_attachments:
                if item[0] == 'photos_list':
                    count += 9  # photos_list уже добавлен как 10, но мы его пересчитываем
        
        # Формируем итоговую строку вложений
        for item in other_attachments:
            if len(attach) > 0:
                attach += ','
            attach += f"{item[0]}{item[1]}{item[2]}{item[3]}"
        
        if has_video and video_attachments:
            for item in video_attachments:
                if len(attach) > 0:
                    attach += ','
                attach += f"{item[0]}{item[1]}{item[2]}{item[3]}"
        elif has_audio and audio_attachments:
            for item in audio_attachments:
                if len(attach) > 0:
                    attach += ','
                attach += f"{item[0]}{item[1]}{item[2]}{item[3]}"
        
        return attach, count
    else:
        return '', 0


if __name__ == '__main__':
    pass
