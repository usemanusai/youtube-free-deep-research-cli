from pathlib import Path
from youtube_chat_cli_main.services.vector_store import get_vector_store

out_path = Path('ingest_report.txt')
try:
    vs = get_vector_store()
    info = {}
    # Try a few known methods depending on implementation
    if hasattr(vs, 'get_collection_info'):
        info = vs.get_collection_info()
    elif hasattr(vs, 'info'):
        info = vs.info()
    else:
        # Fallback: try a simple search to infer if empty
        try:
            res = vs.search('test', top_k=1)
            info = {'search_sample_count': len(res)}
        except Exception as e:
            info = {'error': f'search failed: {e!r}'}
    out_path.write_text(str(info), encoding='utf-8')
except Exception as e:
    out_path.write_text(f'ERR: {e!r}', encoding='utf-8')

