from flask import Flask, render_template, request, jsonify, send_file
import genanki
import random
import os
import tempfile
import shutil
import glob
from gtts import gTTS
from g2p_en import G2p
import requests
import re
from typing import List, Tuple
import json

# Убери template_folder='.'
app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

class WordProcessor:
    def __init__(self):
        self.transcription_cache = {}
    
    def get_transcription(self, word: str) -> str:
        """Генерирует транскрипцию используя простые правила"""
        try:
            # Простая транскрипция на основе правил
            word_lower = word.lower()
            
            # Кэшируем результаты
            if word_lower in self.transcription_cache:
                return self.transcription_cache[word_lower]
            
            # Простые правила транскрипции для распространенных слов
            common_transcriptions = {
                'hello': '[həˈloʊ]',
                'goodbye': '[ɡʊdˈbaɪ]',
                'thank you': '[θæŋk juː]',
                'please': '[pliːz]',
                'sorry': '[ˈsɒri]',
                'yes': '[jɛs]',
                'no': '[noʊ]',
                'maybe': '[ˈmeɪbi]',
                'today': '[təˈdeɪ]',
                'tomorrow': '[təˈmɒroʊ]',
                'yesterday': '[ˈjɛstərdeɪ]',
                'monday': '[ˈmʌndeɪ]',
                'tuesday': '[ˈtjuːzdeɪ]',
                'wednesday': '[ˈwɛnzdeɪ]',
                'thursday': '[ˈθɜːzdeɪ]',
                'friday': '[ˈfraɪdeɪ]',
                'saturday': '[ˈsætədeɪ]',
                'sunday': '[ˈsʌndeɪ]',
                'january': '[ˈdʒænjuəri]',
                'february': '[ˈfɛbruəri]',
                'march': '[mɑːrtʃ]',
                'april': '[ˈeɪprəl]',
                'may': '[meɪ]',
                'june': '[dʒuːn]',
                'july': '[dʒuːˈlaɪ]',
                'august': '[ˈɔːɡəst]',
                'september': '[sɛpˈtɛmbər]',
                'october': '[ɒkˈtoʊbər]',
                'november': '[noʊˈvɛmbər]',
                'december': '[dɪˈsɛmbər]',
                'spring': '[sprɪŋ]',
                'summer': '[ˈsʌmər]',
                'autumn': '[ˈɔːtəm]',
                'winter': '[ˈwɪntər]',
                'time': '[taɪm]',
                'clock': '[klɒk]',
                'hour': '[ˈaʊər]',
                'minute': '[ˈmɪnɪt]',
                'second': '[ˈsɛkənd]',
                'year': '[jɪər]',
                'month': '[mʌnθ]',
                'week': '[wiːk]',
                'day': '[deɪ]',
                'morning': '[ˈmɔːrnɪŋ]',
                'afternoon': '[ˌæftərˈnuːn]',
                'evening': '[ˈiːvnɪŋ]',
                'night': '[naɪt]',
                'noon': '[nuːn]',
                'midnight': '[ˈmɪdnaɪt]',
                'dawn': '[dɔːn]',
                'dusk': '[dʌsk]'
            }
            
            # Ищем в общих транскрипциях
            if word_lower in common_transcriptions:
                transcription = common_transcriptions[word_lower]
            else:
                # Генерируем простую транскрипцию по правилам
                transcription = self.generate_simple_transcription(word)
            
            self.transcription_cache[word_lower] = transcription
            return transcription
            
        except:
            return "[transcription]"
    
    def generate_simple_transcription(self, word: str) -> str:
        """Генерирует простую транскрипцию на основе базовых правил"""
        word_lower = word.lower()
        
        # Простые правила для распространенных окончаний и паттернов
        rules = [
            (r'ing$', 'ɪŋ'),
            (r'ed$', 'd'),
            (r's$', 's'),
            (r'th$', 'θ'),
            (r'^un', 'ʌn'),
            (r'^re', 'riː'),
            (r'^dis', 'dɪs'),
            (r'^pre', 'priː'),
        ]
        
        # Применяем правила
        transcribed = word_lower
        for pattern, replacement in rules:
            transcribed = re.sub(pattern, replacement, transcribed)
        
        return f"[{transcribed}]"
    
    def get_simple_context(self, word: str) -> str:
        """Простой контекст на основе типа слова"""
        word_lower = word.lower()
        
        # Простая эвристика для базового контекста
        if any(month in word_lower for month in ['january', 'february', 'march', 'april', 'may', 'june', 
                                               'july', 'august', 'september', 'october', 'november', 'december']):
            return "name of month"
        
        if any(day in word_lower for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
            return "day of week"
        
        if any(season in word_lower for season in ['spring', 'summer', 'autumn', 'fall', 'winter']):
            return "season of the year"
        
        if any(time_word in word_lower for time_word in ['time', 'clock', 'hour', 'minute', 'second', 'year', 'month', 'week', 'day']):
            return "time related word"
        
        if len(word.split()) > 1:  # Если это фраза
            return "common English phrase"
        
        return "basic English vocabulary"

    def process_word_pair(self, russian: str, english: str) -> List:
        """Обрабатывает пару слов, генерируя транскрипцию и контекст"""
        transcription = self.get_transcription(english)
        context = self.get_simple_context(english)
        
        return [russian.strip(), english.strip(), context, transcription]
# Инициализируем процессор слов
word_processor = WordProcessor()

# Остальные функции остаются без изменений
def get_audio_gtts(word, audio_dir):
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    audio_filename = f"{word.replace(' ', '_').replace('/', '_').replace('\\', '_')}.mp3"
    audio_path = os.path.join(audio_dir, audio_filename)
    
    if os.path.exists(audio_path):
        return audio_filename
    
    try:
        tts = gTTS(text=word, lang='en', slow=False)
        tts.save(audio_path)
        print(f"✓ Аудио для '{word}' создано через gTTS")
        return audio_filename
    except Exception as e:
        print(f"✗ Ошибка gTTS для '{word}': {e}")
        return None

def get_english_audio(word, audio_dir, method="gtts"):
    if method == "gtts":
        return get_audio_gtts(word, audio_dir)
    else:
        return get_audio_gtts(word, audio_dir)

def create_anki_deck_from_data(data, deck_name, temp_dir):
    """Создает колоду Anki из данных"""
    # Создаем временные папки
    audio_dir = os.path.join(temp_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # Создаем колоду
    my_deck = genanki.Deck(
        random.randrange(1 << 30, 1 << 31),
        deck_name
    )

    my_model = genanki.Model(
        random.randrange(1 << 30, 1 << 31),
        'English Word Card with Audio',
        fields=[
            {'name': 'Russian'},
            {'name': 'English'},
            {'name': 'Context'},
            {'name': 'Transcription'},
            {'name': 'Audio'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '''
                    <div style="text-align: center; font-size: 24px; margin: 20px;">
                        {{Russian}}
                    </div>
                    <div style="text-align: center; color: gray; font-size: 16px;">
                        Введите английский перевод:
                    </div>
                    <div style="text-align: center; margin: 20px;">
                        {{type:English}}
                    </div>
                ''',
                'afmt': '''
                    <div style="text-align: center; font-size: 24px; margin: 20px;">
                        {{Russian}}
                    </div>
                    <hr>
                    <div style="text-align: center; margin: 20px;">
                        <strong>Ваш ответ:</strong> {{type:English}}
                    </div>
                    <div style="text-align: center; font-size: 20px; color: blue; margin: 10px;">
                        <strong>Правильно:</strong> {{English}}
                    </div>
                    <div style="text-align: center; color: purple; margin: 10px;">
                        <strong>Транскрипция:</strong> {{Transcription}}
                    </div>
                    <div style="text-align: center; margin: 15px;">
                        {{Audio}}
                    </div>
                    <div style="text-align: center; color: gray; font-size: 14px; margin: 10px;">
                        {{Context}}
                    </div>
                ''',
            },
        ],
        css='''
            .card {
                font-family: arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
            }
        '''
    )

    print("🚀 Создание аудио файлов через gTTS...")
    media_files = []
    
    # Сначала создаем все аудио файлы
    for i, (russian, english, context, transcription) in enumerate(data):
        print(f"[{i+1}/{len(data)}] Получение аудио для: {english}")
        
        audio_filename = get_english_audio(english, audio_dir, method="gtts")
        
        if audio_filename:
            audio_path = os.path.join(audio_dir, audio_filename)
            if os.path.exists(audio_path):
                media_files.append(audio_path)
                print(f"   ✅ Успешно: {audio_filename}")
            else:
                print(f"   ❌ Файл не создан: {english}")
        else:
            print(f"   ❌ Не удалось создать аудио: {english}")

    print(f"\n📝 Создание карточек...")
    # Создаем карточки
    successful_cards = 0
    for russian, english, context, transcription in data:
        audio_filename = f"{english.replace(' ', '_')}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)
        
        if os.path.exists(audio_path):
            audio_field = f'[sound:{audio_filename}]'
            successful_cards += 1
        else:
            audio_field = ''
            print(f"   ⚠ Аудио для '{english}' не найдено")
        
        note = genanki.Note(
            model=my_model,
            fields=[russian, english, context, transcription, audio_field]
        )
        my_deck.add_note(note)

    # Создаем пакет и добавляем аудио файлы
    package = genanki.Package(my_deck)
    
    if os.path.exists(audio_dir):
        all_audio_files = glob.glob(os.path.join(audio_dir, "*.mp3"))
        package.media_files = all_audio_files
        print(f"✅ Добавлено {len(all_audio_files)} аудио файлов в пакет")
    
    # Сохраняем колоду
    safe_deck_name = "".join(c for c in deck_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe_deck_name.replace(' ', '_')}.apkg"
    deck_path = os.path.join(temp_dir, filename)
    
    package.write_to_file(deck_path)
    
    print(f"\n🎉 Колода успешно создана!")
    print(f"📁 Файл: {filename}")
    print(f"🎵 Аудио файлов: {len(media_files)}")
    print(f"📊 Карточек с аудио: {successful_cards}/{len(data)}")
    print(f"📊 Всего карточек: {len(data)}")
    
    return deck_path

@app.route('/')
def index():
    return render_template('anki.html')

@app.route('/generate_deck', methods=['POST'])
def generate_deck():
    temp_dir = tempfile.mkdtemp()
    
    try:
        input_method = request.form.get('input_method')
        deck_name = request.form.get('deck_name', 'English-Russian Deck')
        
        word_pairs = []
        
        if input_method == 'text':
            english_text = request.form.get('english_text', '')
            russian_text = request.form.get('russian_text', '')
            
            english_lines = [line.strip() for line in english_text.split('\n') if line.strip()]
            russian_lines = [line.strip() for line in russian_text.split('\n') if line.strip()]
            
            # Обрабатываем каждую пару слов
            for eng, rus in zip(english_lines, russian_lines):
                processed_pair = word_processor.process_word_pair(rus, eng)
                word_pairs.append(processed_pair)
                
        elif input_method == 'file':
            english_file = request.files.get('english_file')
            russian_file = request.files.get('russian_file')
            
            if english_file and russian_file:
                english_content = english_file.read().decode('utf-8')
                russian_content = russian_file.read().decode('utf-8')
                
                english_lines = [line.strip() for line in english_content.split('\n') if line.strip()]
                russian_lines = [line.strip() for line in russian_content.split('\n') if line.strip()]
                
                for eng, rus in zip(english_lines, russian_lines):
                    processed_pair = word_processor.process_word_pair(rus, eng)
                    word_pairs.append(processed_pair)
        
        if not word_pairs:
            return jsonify({
                'success': False,
                'error': 'Нет данных для создания колоды'
            }), 400
        
        # СОЗДАЕМ РЕАЛЬНУЮ КОЛОДУ
        deck_path = create_anki_deck_from_data(word_pairs, deck_name, temp_dir)
        
        # Возвращаем файл для скачивания
        return send_file(
            deck_path,
            as_attachment=True,
            download_name=f'{deck_name}.apkg',
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка при создании колоды: {str(e)}'
        }), 500
    finally:
        # Очищаем временные файлы
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)