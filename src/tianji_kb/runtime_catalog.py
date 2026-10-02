"""Build-time source review; production only consumes the reviewed release artifact."""
import hashlib,json,os
from pathlib import Path
from .knowledge import read_json

class RuntimeUnavailable(ValueError):
    pass

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def release_paths(root):
    paths=set((root/'data/canonical').rglob('*.json'))
    paths.update((root/'schemas/knowledge').glob('*.json'))
    paths.update((root/'src/tianji_kb').rglob('*.py'))
    for name in ['domain_registry.json','knowledge_sources.json','phase2_source_audit.json','phase2_rule_promotions.json','phase1_protected_files.json']:
        paths.add(root/'config'/name)
    return sorted(paths)

def build_catalog(root):
    from .resolver import EvidenceResolver
    root=Path(root).resolve()
    resolver=EvidenceResolver(root,review_sources=True)
    payload={'model':resolver.model,'contracts':resolver.contracts,
             'supplementary_classics':resolver.supplementary_classics,
             'supplementary_records':resolver.supplementary_records}
    # Hash only repository-controlled Canonical, configuration, schemas and code.
    manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in release_paths(root)}
    artifact={'schema_version':'1.0','model':'phase3-production-runtime','manifest':manifest,
              'payload':payload,'payload_sha256':digest(payload),'manifest_sha256':digest(manifest)}
    path=root/'build/production_runtime.json';path.parent.mkdir(exist_ok=True)
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(artifact,ensure_ascii=False,separators=(',',':'))+'\n')
    os.replace(temporary,path)
    return artifact

def load_catalog(root):
    root=Path(root).resolve();path=root/'build/production_runtime.json'
    if not path.is_file():raise RuntimeUnavailable('Build the reviewed production runtime before serving requests')
    try:
        artifact=read_json(path)
        if artifact['model']!='phase3-production-runtime' or artifact['schema_version']!='1.0':
            raise RuntimeUnavailable('Unsupported production runtime version')
        if digest(artifact['payload'])!=artifact['payload_sha256'] or digest(artifact['manifest'])!=artifact['manifest_sha256']:
            raise RuntimeUnavailable('Production runtime integrity check failed')
        expected={str(p.relative_to(root)) for p in release_paths(root)}
        if set(artifact['manifest'])!=expected:raise RuntimeUnavailable('Production runtime release files changed; rebuild required')
        for name,checksum in artifact['manifest'].items():
            candidate=(root/name).resolve()
            if not candidate.is_relative_to(root) or not name.startswith(('data/canonical/','config/','schemas/knowledge/','src/tianji_kb/')) or not str(candidate.relative_to(root)).startswith(('data/canonical/','config/','schemas/knowledge/','src/tianji_kb/')):
                raise RuntimeUnavailable('Unsafe runtime manifest path')
            if hashlib.sha256(candidate.read_bytes()).hexdigest()!=checksum:
                raise RuntimeUnavailable('Production runtime is stale; rebuild required')
        return artifact['payload']
    except RuntimeUnavailable:raise
    except (OSError,KeyError,TypeError,ValueError) as error:
        raise RuntimeUnavailable('Production runtime is invalid; rebuild required') from error
