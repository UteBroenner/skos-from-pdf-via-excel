from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.12.0"
version = "0.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'svv',
     'default_range': 'string',
     'description': 'Model of one vocabulary (skos:ConceptScheme) and its concepts '
                    'as captured in SKOS-Excel-mal-v8. Code lists (kodeverk) are '
                    'not modelled here. Each slot is annotated with its v8 Excel '
                    'column (excel_column) and the technical column name in row 22 '
                    '(excel_name), which is also intended as the SharePoint List '
                    'internal column name. Language tags (in_language) and enum '
                    "meanings are applied by the project's RDF writer "
                    '(vocabtool/linkml_rdf.py); the standard LinkML RDF dumper '
                    'ignores them.',
     'id': 'http://example.org/vegvesen/vokabular/def/schema',
     'imports': ['linkml:types'],
     'license': 'CC-BY-4.0',
     'name': 'svv_vokabular',
     'prefixes': {'adms': {'prefix_prefix': 'adms',
                           'prefix_reference': 'http://www.w3.org/ns/adms#'},
                  'concept_status': {'prefix_prefix': 'concept_status',
                                     'prefix_reference': 'http://publications.europa.eu/resource/authority/concept-status/'},
                  'dcat': {'prefix_prefix': 'dcat',
                           'prefix_reference': 'http://www.w3.org/ns/dcat#'},
                  'dct': {'prefix_prefix': 'dct',
                          'prefix_reference': 'http://purl.org/dc/terms/'},
                  'euvoc': {'prefix_prefix': 'euvoc',
                            'prefix_reference': 'http://publications.europa.eu/ontology/euvoc#'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'owl': {'prefix_prefix': 'owl',
                          'prefix_reference': 'http://www.w3.org/2002/07/owl#'},
                  'skos': {'prefix_prefix': 'skos',
                           'prefix_reference': 'http://www.w3.org/2004/02/skos/core#'},
                  'skosno': {'prefix_prefix': 'skosno',
                             'prefix_reference': 'https://data.norge.no/vocabulary/skosno#'},
                  'svv': {'prefix_prefix': 'svv',
                          'prefix_reference': 'http://example.org/vegvesen/vokabular/def#'},
                  'vok': {'prefix_prefix': 'vok',
                          'prefix_reference': 'http://example.org/vegvesen/vokabular/'},
                  'xkos': {'prefix_prefix': 'xkos',
                           'prefix_reference': 'http://rdf-vocabulary.ddialliance.org/xkos#'}},
     'source_file': 'schema/svv_vokabular.yaml',
     'title': 'SKOS-vokabular (Excel-mal v8)'} )

class ConceptStatus(str, Enum):
    """
    Status values from the template's statusliste, mapped to the EU concept-status authority table.
    """
    kandidat = "kandidat"
    gjeldende = "gjeldende"
    utdatert = "utdatert"
    forkastet = "forkastet"



class ConceptScheme(ConfiguredBaseModel):
    """
    One vocabulary = one Excel workbook (vokabular sheet, rows 1-16).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'skos:ConceptScheme',
         'from_schema': 'http://example.org/vegvesen/vokabular/def/schema',
         'tree_root': True})

    uri: str = Field(default=..., description="""Concept or scheme URI. For concepts: <scheme URI>/<concept name>, where column B of the workbook holds only the CamelCase concept name (e.g. Rekkverk, or DoubleCrochet-ENUS with a language suffix when the term means another concept in another language) and the tools build the URI.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'B'},
                         'excel_name': {'tag': 'excel_name', 'value': 'begrep'},
                         'excel_value': {'tag': 'excel_value',
                                         'value': 'CamelCase concept name only'}},
         'domain_of': ['ConceptScheme', 'Concept']} })
    kortnavn: str = Field(default=..., description="""Short name of the vocabulary, max 4 letters or digits (cell B12).""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_cell': {'tag': 'excel_cell', 'value': 'B14'}},
         'domain_of': ['ConceptScheme'],
         'slot_uri': 'svv:kortnavn'} })
    title: str = Field(default=..., json_schema_extra = { "linkml_meta": {'annotations': {'excel_cell': {'tag': 'excel_cell', 'value': 'B15'}},
         'domain_of': ['ConceptScheme'],
         'in_language': 'nb',
         'slot_uri': 'dct:title'} })
    main_language: Optional[str] = Field(default=None, description="""BCP 47 tag of the language in which every concept must have a prefLabel and a definition (scheme row \"hovedspråk\"; default nb). Enforced by SHACL (shapes/cross_row.shacl.ttl).""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_label': {'tag': 'excel_label', 'value': 'hovedspråk'}},
         'domain_of': ['ConceptScheme'],
         'slot_uri': 'svv:mainLanguage'} })
    creator: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_cell': {'tag': 'excel_cell', 'value': 'B16'}},
         'domain_of': ['ConceptScheme'],
         'slot_uri': 'dct:creator'} })
    publisher: Optional[str] = Field(default=None, description="""System-generated at publication.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_cell': {'tag': 'excel_cell', 'value': 'B17'}},
         'domain_of': ['ConceptScheme'],
         'slot_uri': 'dct:publisher'} })
    issued: Optional[date] = Field(default=None, description="""System-generated at publication.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_cell': {'tag': 'excel_cell', 'value': 'B18'}},
         'domain_of': ['ConceptScheme'],
         'slot_uri': 'dct:issued'} })
    concepts: Optional[list[Concept]] = Field(default=None, description="""Container slot for the data file only. Not written to RDF; the RDF writer emits skos:inScheme on each concept instead.""", json_schema_extra = { "linkml_meta": {'annotations': {'rdf_skip': {'tag': 'rdf_skip', 'value': True}},
         'domain_of': ['ConceptScheme'],
         'slot_uri': 'svv:concepts'} })

    @field_validator('kortnavn')
    def pattern_kortnavn(cls, v):
        pattern=re.compile(r"^[A-Za-z0-9]{1,4}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid kortnavn format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid kortnavn format: {v}"
            raise ValueError(err_msg)
        return v


class Concept(ConfiguredBaseModel):
    """
    One row in the vokabular sheet (row 23 onwards).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'skos:Concept',
         'from_schema': 'http://example.org/vegvesen/vokabular/def/schema'})

    uri: str = Field(default=..., description="""Concept or scheme URI. For concepts: <scheme URI>/<concept name>, where column B of the workbook holds only the CamelCase concept name (e.g. Rekkverk, or DoubleCrochet-ENUS with a language suffix when the term means another concept in another language) and the tools build the URI.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'B'},
                         'excel_name': {'tag': 'excel_name', 'value': 'begrep'},
                         'excel_value': {'tag': 'excel_value',
                                         'value': 'CamelCase concept name only'}},
         'domain_of': ['ConceptScheme', 'Concept']} })
    identifier: str = Field(default=..., description="""Internal ID <kortnavn>-NNNN. Relations in Excel refer to this ID.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'A'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'intern_identifikator'},
                         'requirement': {'tag': 'requirement',
                                         'value': 'obligatorisk'}},
         'domain_of': ['Concept'],
         'slot_uri': 'dct:identifier'} })
    pref_label_nb: Optional[str] = Field(default=None, description="""Recommended term, bokmål. Lowercase except acronyms (S05). Required when the main language is nb (SHACL rule).""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'C'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'anbefalt_term_bokmål'},
                         'requirement': {'tag': 'requirement',
                                         'value': 'obligatorisk'}},
         'domain_of': ['Concept'],
         'in_language': 'nb',
         'slot_uri': 'skos:prefLabel'} })
    pref_label_en: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'D'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'anbefalt_term_engelsk'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'in_language': 'en',
         'slot_uri': 'skos:prefLabel'} })
    pref_label_nn: Optional[str] = Field(default=None, description="""Obligatory in the template, but left empty by extraction for the expert (S06).""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'E'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'anbefalt_term_nynorsk'},
                         'requirement': {'tag': 'requirement',
                                         'value': 'obligatorisk'}},
         'domain_of': ['Concept'],
         'in_language': 'nn',
         'slot_uri': 'skos:prefLabel'} })
    notation: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'F'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'notasjon_eller_kode'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skos:notation'} })
    definition_nb: Optional[str] = Field(default=None, description="""Required when the main language is nb (SHACL rule).""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'G'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'definisjon_bokmål'},
                         'requirement': {'tag': 'requirement',
                                         'value': 'obligatorisk'}},
         'domain_of': ['Concept'],
         'in_language': 'nb',
         'slot_uri': 'skos:definition'} })
    definition_en: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'H'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'definisjon_engelsk'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'in_language': 'en',
         'slot_uri': 'skos:definition'} })
    definition_nn: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'I'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'definisjon_nynorsk'},
                         'requirement': {'tag': 'requirement',
                                         'value': 'obligatorisk'}},
         'domain_of': ['Concept'],
         'in_language': 'nn',
         'slot_uri': 'skos:definition'} })
    alt_label_nb: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'J'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'tillat_term_bokmål'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'},
                         'separator': {'tag': 'separator', 'value': ','}},
         'domain_of': ['Concept'],
         'in_language': 'nb',
         'slot_uri': 'skos:altLabel'} })
    alt_label_en: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'L'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'tillat_term_engelsk'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'},
                         'separator': {'tag': 'separator', 'value': ','}},
         'domain_of': ['Concept'],
         'in_language': 'en',
         'slot_uri': 'skos:altLabel'} })
    alt_label_nn: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'K'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'tillat_term_nynorsk'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'},
                         'separator': {'tag': 'separator', 'value': ','}},
         'domain_of': ['Concept'],
         'in_language': 'nn',
         'slot_uri': 'skos:altLabel'} })
    audience: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'M'},
                         'excel_name': {'tag': 'excel_name', 'value': 'målgruppe'}},
         'domain_of': ['Concept'],
         'slot_uri': 'dct:audience'} })
    source: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'N'},
                         'excel_name': {'tag': 'excel_name', 'value': 'kilde'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'dct:source'} })
    relationship_with_source: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'O'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'forhold_til_kilde'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skosno:relationshipWithSource'} })
    scope_note: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'P'},
                         'excel_name': {'tag': 'excel_name', 'value': 'merknad'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'}},
         'domain_of': ['Concept'],
         'in_language': 'nb',
         'slot_uri': 'skos:scopeNote'} })
    editorial_note: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'Q'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'merknad_til_etableringmåte'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skos:editorialNote'} })
    example: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'R'},
                         'excel_name': {'tag': 'excel_name', 'value': 'eksempel'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skos:example'} })
    subject: Optional[str] = Field(default=None, description="""Subject area. Template allows rdf:langString or skos:Concept; modelled as text for now.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'S'},
                         'excel_name': {'tag': 'excel_name', 'value': 'fagområde'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'}},
         'domain_of': ['Concept'],
         'in_language': 'nb',
         'slot_uri': 'dct:subject'} })
    hidden_label: Optional[str] = Field(default=None, description="""Discouraged term, e.g. a common misspelling.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'T'},
                         'excel_name': {'tag': 'excel_name', 'value': 'frarådd_term'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'in_language': 'nb',
         'slot_uri': 'skos:hiddenLabel'} })
    broader: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'U'},
                         'excel_name': {'tag': 'excel_name', 'value': 'har_overbegrep'},
                         'excel_value': {'tag': 'excel_value', 'value': 'identifier'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skos:broader'} })
    is_part_of: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'V'},
                         'excel_name': {'tag': 'excel_name', 'value': 'er_del_av'},
                         'excel_value': {'tag': 'excel_value', 'value': 'identifier'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'xkos:isPartOf'} })
    related: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'W'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'er_relatert_til'},
                         'excel_value': {'tag': 'excel_value', 'value': 'identifier'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'separator': {'tag': 'separator', 'value': ','}},
         'domain_of': ['Concept'],
         'slot_uri': 'skos:related'} })
    relation_role: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'X'},
                         'excel_name': {'tag': 'excel_name', 'value': 'relasjonsrolle'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'}},
         'domain_of': ['Concept'],
         'in_language': 'nb',
         'slot_uri': 'skosno:relationRole'} })
    exact_match: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'Y'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'har_eksakt_samsvar_med'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skos:exactMatch'} })
    close_match: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'Z'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'har_nært_samsvar_med'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skos:closeMatch'} })
    contact_point: str = Field(default=..., description="""E-mail address or web address. Vegvesen vocabularies use datagovernance@vegvesen.no (fixed value in the field instructions); the schema accepts any address.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AA'},
                         'excel_name': {'tag': 'excel_name', 'value': 'kontaktpunkt'},
                         'requirement': {'tag': 'requirement',
                                         'value': 'obligatorisk'}},
         'domain_of': ['Concept'],
         'slot_uri': 'dcat:contactPoint'} })
    created: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AC'},
                         'excel_name': {'tag': 'excel_name', 'value': 'dato_opprettet'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'}},
         'domain_of': ['Concept'],
         'slot_uri': 'dct:created'} })
    created_by: Optional[str] = Field(default=None, description="""Hidden column; template formula = dct:creator of the vocabulary (cell B16).""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AD'},
                         'excel_name': {'tag': 'excel_name', 'value': 'opprettet_av'},
                         'hidden': {'tag': 'hidden', 'value': True}},
         'domain_of': ['Concept'],
         'slot_uri': 'dct:contributor'} })
    modified: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AE'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'dato_sist_endret'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'}},
         'domain_of': ['Concept'],
         'slot_uri': 'dct:modified'} })
    modified_by: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AF'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'sist_endret_av'}},
         'domain_of': ['Concept'],
         'slot_uri': 'dct:contributor'} })
    version_info: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AG'},
                         'excel_name': {'tag': 'excel_name', 'value': 'versjonsnummer'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'owl:versionInfo'} })
    version_notes: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AH'},
                         'excel_name': {'tag': 'excel_name', 'value': 'versjonsnote'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'adms:versionNotes'} })
    status: Optional[ConceptStatus] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AI'},
                         'excel_name': {'tag': 'excel_name', 'value': 'status'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'}},
         'domain_of': ['Concept'],
         'slot_uri': 'euvoc:status'} })
    start_date: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AJ'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'gjelder_fra_og_med'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'}},
         'domain_of': ['Concept'],
         'slot_uri': 'euvoc:startDate'} })
    end_date: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AK'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'gjelder_til_og_med'},
                         'requirement': {'tag': 'requirement', 'value': 'anbefalt'}},
         'domain_of': ['Concept'],
         'slot_uri': 'euvoc:endDate'} })
    data_structure_label: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AL'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'datastrukturterm'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skosno:dataStructureLabel'} })
    value_range: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AM'},
                         'excel_name': {'tag': 'excel_name', 'value': 'verdiområde'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'}},
         'domain_of': ['Concept'],
         'slot_uri': 'skosno:valueRange'} })
    tier: Optional[int] = Field(default=None, description="""1 = physical objects, spatial concepts, measurable properties; 2 = processes and states; 3 = normative requirements. Only Tier 1 becomes OWL classes.""", ge=1, le=3, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column',
                                          'value': 'AN (base template), AX (language '
                                                   'extension): always the last '
                                                   'column, outside the Excel table'},
                         'excel_name': {'tag': 'excel_name', 'value': 'tier'},
                         'requirement': {'tag': 'requirement', 'value': 'internt'}},
         'domain_of': ['Concept'],
         'slot_uri': 'svv:tier'} })
    pref_label_en_us: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AN'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'anbefalt_term_engelsk_us'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'en-US',
         'slot_uri': 'skos:prefLabel'} })
    pref_label_en_gb: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AO'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'anbefalt_term_engelsk_gb'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'en-GB',
         'slot_uri': 'skos:prefLabel'} })
    pref_label_de: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AP'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'anbefalt_term_tysk'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'de',
         'slot_uri': 'skos:prefLabel'} })
    pref_label_es: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AQ'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'anbefalt_term_spansk'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'es',
         'slot_uri': 'skos:prefLabel'} })
    alt_label_en_us: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AR'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'tillat_term_engelsk_us'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'separator': {'tag': 'separator', 'value': ','},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'en-US',
         'slot_uri': 'skos:altLabel'} })
    alt_label_en_gb: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AS'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'tillat_term_engelsk_gb'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'separator': {'tag': 'separator', 'value': ','},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'en-GB',
         'slot_uri': 'skos:altLabel'} })
    alt_label_de: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AT'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'tillat_term_tysk'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'separator': {'tag': 'separator', 'value': ','},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'de',
         'slot_uri': 'skos:altLabel'} })
    alt_label_es: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AU'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'tillat_term_spansk'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'separator': {'tag': 'separator', 'value': ','},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'es',
         'slot_uri': 'skos:altLabel'} })
    definition_en_us: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AV'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'definisjon_engelsk_us'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'en-US',
         'slot_uri': 'skos:definition'} })
    scope_note_en_us: Optional[str] = Field(default=None, description="""Usage note in US English, e.g. a warning that a term means another concept elsewhere.""", json_schema_extra = { "linkml_meta": {'annotations': {'excel_column': {'tag': 'excel_column', 'value': 'AW'},
                         'excel_name': {'tag': 'excel_name',
                                        'value': 'merknad_engelsk_us'},
                         'requirement': {'tag': 'requirement', 'value': 'valgfri'},
                         'template': {'tag': 'template', 'value': 'v8-lang-ext'}},
         'domain_of': ['Concept'],
         'in_language': 'en-US',
         'slot_uri': 'skos:scopeNote'} })
    in_scheme: Optional[str] = Field(default=None, description="""Set by the converter from the scheme URI.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Concept'], 'slot_uri': 'skos:inScheme'} })

    @field_validator('identifier')
    def pattern_identifier(cls, v):
        pattern=re.compile(r"^[A-Za-z0-9]{1,4}-\d{4}$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid identifier format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid identifier format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('contact_point')
    def pattern_contact_point(cls, v):
        pattern=re.compile(r"^([^@\s]+@[^@\s]+\.[A-Za-z]{2,}|https?://\S+)$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid contact_point format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid contact_point format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('created_by')
    def pattern_created_by(cls, v):
        pattern=re.compile(r"^[^@\s]+@vegvesen\.no$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid created_by format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid created_by format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('modified_by')
    def pattern_modified_by(cls, v):
        pattern=re.compile(r"^[^@\s]+@vegvesen\.no$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.search(element):
                    err_msg = f"Invalid modified_by format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.search(v):
            err_msg = f"Invalid modified_by format: {v}"
            raise ValueError(err_msg)
        return v


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ConceptScheme.model_rebuild()
Concept.model_rebuild()
