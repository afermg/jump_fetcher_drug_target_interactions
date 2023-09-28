from zipfile import ZipFile
from pathlib import Path

import pandas as pd
from jump.uniprot import get_gene_names

from jump.utils import download_file


def open_zip(output_path: Path, redownload=False):
    filepath = output_path / 'biokg/biokg.zip'
    url = 'https://github.com/dsi-bdi/biokg/releases/download/v1.0.0/biokg.zip'
    download_file(url, filepath, redownload)

    with ZipFile(filepath, 'r') as zipfile:
        fread = zipfile.open('biokg.links.tsv')
        edges = pd.read_csv(fread,
                            sep='\t',
                            low_memory=False,
                            names=['source', 'rel_type', 'target'])
    return edges


def get_compound_annotations(output_dir: str):
    rel_types = [
        'DPI', 'DRUG_CARRIER', 'DRUG_DISEASE_ASSOCIATION', 'DRUG_ENZYME',
        'DRUG_PATHWAY_ASSOCIATION', 'DRUG_TARGET', 'DRUG_TRANSPORTER'
    ]
    edges = open_zip(Path(output_dir)).query('rel_type in @rel_types')
    uniprot_ids = edges['target'].drop_duplicates().tolist()
    results = get_gene_names(uniprot_ids)
    uniprot_to_gene = {r['from']: r['to'] for r in results['results']}
    edges['target'] = edges['target'].map(uniprot_to_gene)
    edges.dropna(subset=['target'], inplace=True)
    edges.drop_duplicates(inplace=True)
    edges['source_id'] = 'drugbank'
    return edges[['source', 'target', 'rel_type', 'source_id']]
