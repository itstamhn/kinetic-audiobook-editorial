#!/usr/bin/env python3
import os
import sys
import re
import json
import argparse
import whisper
from literary_vocab_engine import extract_literary_vocabulary
from wordfreq import zipf_frequency

def main():
    parser = argparse.ArgumentParser(description='Universal Audiobook Chapter Video Producer')
    parser.add_argument('--audio', required=True, help='Path to audiobook MP3/M4A audio file')
    parser.add_argument('--book-title', required=True, help='Title of the book (e.g. Dune)')
    parser.add_argument('--chapter-title', required=True, help='Chapter title (e.g. Chapter 1)')
    parser.add_argument('--author', default='Unknown Author', help='Author of the book')
    parser.add_argument('--narrator', default='Uncredited Narrator', help='Audiobook narrator')
    parser.add_argument('--out-props', default=None, help='Output props JSON file path')
    parser.add_argument('--whisper-model', default='base.en', help='Whisper AI model')
    parser.add_argument('--words-per-slide', type=int, default=18, help='Max words per editorial slide')
    parser.add_argument('--exclude-names', nargs='*', default=[], help='Character names to exclude')
    
    args = parser.parse_args()
    
    audio_path = os.path.abspath(args.audio)
    if not os.path.exists(audio_path):
        print(f'Error: Audio file not found at {audio_path}')
        sys.exit(1)
        
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', f'{args.book_title}_{args.chapter_title}').lower()
    os.makedirs('chapters_data', exist_ok=True)
    os.makedirs('out', exist_ok=True)
    
    whisper_cache = f'chapters_data/{slug}_whisper.json'
    props_output = args.out_props or f'chapters_data/{slug}_props.json'
    
    # 1. Transcribe with Whisper AI
    if os.path.exists(whisper_cache):
        print(f'Loading cached Whisper timestamps: {whisper_cache}')
        with open(whisper_cache, 'r', encoding='utf-8') as f:
            whisper_words = json.load(f)
    else:
        print(f'Transcribing audio with Whisper AI ({args.whisper_model})...')
        model = whisper.load_model(args.whisper_model)
        result = model.transcribe(audio_path, word_timestamps=True, language='en')
        
        whisper_words = []
        for seg in result['segments']:
            for w in seg.get('words', []):
                whisper_words.append({
                    'word': w['word'].strip(),
                    'start': round(w['start'], 3),
                    'end': round(w['end'], 3)
                })
        with open(whisper_cache, 'w', encoding='utf-8') as f:
            json.dump(whisper_words, f, indent=2)
        print(f'Transcribed {len(whisper_words)} words.')
        
    total_duration = whisper_words[-1]['end'] + 1.0
    
    # 2. Extract C1/C2 & Literary Vocabulary
    name_blacklist = set(n.lower().strip() for n in args.exclude_names)
    print('Extracting vocabulary with Literary & C1/C2 Engine...')
    vocab_data = extract_literary_vocabulary(whisper_words, custom_name_blacklist=name_blacklist)
    unique_vocab = {w: data['translation'] for w, data in vocab_data.items()}
    print(f'Extracted {len(vocab_data)} advanced C1/C2 & Literary vocabulary words.')
    
    # 3. Group Words into Calm Multi-Line Editorial Slides
    pages = []
    current_page_words = []
    
    for idx, w in enumerate(whisper_words):
        clean_w = re.sub(r'[^\w]', '', w['word']).lower()
        vn_gloss = unique_vocab.get(clean_w, None)
        
        current_page_words.append({
            'text': w['word'],
            'start': w['start'],
            'end': w['end'],
            'vn': vn_gloss
        })
        
        is_sentence_end = bool(re.search(r'[.!?]["\']?$', w['word']))
        is_clause_end = bool(re.search(r'[,;:]["\']?$', w['word']))
        
        should_flip = False
        if len(current_page_words) >= args.words_per_slide:
            should_flip = True
        elif len(current_page_words) >= 12 and (is_sentence_end or is_clause_end):
            should_flip = True
        elif is_sentence_end and len(current_page_words) >= 10:
            should_flip = True
        elif idx == len(whisper_words) - 1:
            should_flip = True
            
        if should_flip:
            p_start = current_page_words[0]['start']
            p_end = current_page_words[-1]['end']
            pages.append({
                'id': len(pages) + 1,
                'startTime': p_start,
                'endTime': p_end,
                'words': current_page_words
            })
            current_page_words = []
            
    for i in range(len(pages) - 1):
        mid = (pages[i]['endTime'] + pages[i+1]['startTime']) / 2.0
        pages[i]['endTime'] = mid
        pages[i+1]['startTime'] = mid
    if pages:
        pages[-1]['endTime'] = total_duration
        
    rel_audio_path = os.path.relpath(audio_path, os.path.join(os.getcwd(), 'public')) if 'public' in audio_path else f'chapters_audio/{os.path.basename(audio_path)}'
    
    props_data = {
        'audioSrc': rel_audio_path,
        'audioDuration': total_duration,
        'bookTitle': args.book_title,
        'chapterTitle': args.chapter_title,
        'pages': pages
    }
    
    with open(props_output, 'w', encoding='utf-8') as f:
        json.dump(props_data, f, ensure_ascii=False, indent=2)
        
    print(f'Generated {len(pages)} editorial slides in: {props_output}')
    print(f'Total duration: {total_duration/60:.2f} mins ({int(total_duration*60):,} frames @ 60 FPS).')

if __name__ == '__main__':
    main()
