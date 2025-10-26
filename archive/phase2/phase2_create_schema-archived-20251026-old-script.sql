-- ============================================================================
-- PHASE 2 : Création structure DVF+ 2025-2 dans Supabase
-- ============================================================================

-- 1. Nettoyer ancien schéma (si existe)
DROP SCHEMA IF EXISTS dvf CASCADE;
DROP SCHEMA IF EXISTS dvf_plus_2025_2 CASCADE;

-- 2. Activer extension PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- 3. Créer schéma DVF+ 2025-2
CREATE SCHEMA dvf_plus_2025_2;

-- 4. Créer les 12 tables du modèle DVF+
-- (Structures copiées depuis dvf_plus_init.sql)

CREATE TABLE dvf_plus_2025_2.dvf_plus_adresse (
    idadresse bigint,
    novoie text,
    btq text,
    codvoie text,
    typvoie text,
    voie text,
    codepostal text,
    commune text,
    idadrinvar text,
    coddep text
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_adresse_dispoparc (
    idadresse bigint,
    iddispopar bigint,
    idmutation bigint,
    coddep text
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_adresse_local (
    idadresse bigint,
    iddispoloc bigint,
    idmutation bigint,
    coddep text
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_disposition (
    iddispo bigint,
    idmutation bigint,
    nodispo text,
    valeurfonc numeric,
    nblot numeric,
    coddep text
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_disposition_parcelle (
    iddispopar bigint,
    iddispo bigint,
    idparcelle bigint,
    idmutation bigint,
    idpar text,
    coddep text,
    codcomm text,
    prefsect text,
    nosect text,
    noplan text,
    datemut date,
    anneemut integer,
    moismut integer,
    parcvendue boolean,
    nbmutjour integer,
    nbmutannee integer,
    datemutpre date,
    l_idmutpre text[],
    datemutsui date,
    l_idmutsui text[],
    dcnt01 numeric,
    dcnt02 numeric,
    dcnt03 numeric,
    dcnt04 numeric,
    dcnt05 numeric,
    dcnt06 numeric,
    dcnt07 numeric,
    dcnt08 numeric,
    dcnt09 numeric,
    dcnt10 numeric,
    dcnt11 numeric,
    dcnt12 numeric,
    dcnt13 numeric,
    dcntsol numeric,
    dcntagri numeric,
    dcntnat numeric,
    geomloc public.geometry,
    geompar public.geometry
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_local (
    iddispoloc bigint,
    iddispopar bigint,
    idpar text,
    idmutation bigint,
    idloc text,
    identloc text,
    codtyploc text,
    libtyploc text,
    nbpprinc integer,
    sbati numeric,
    coddep text,
    datemut date,
    anneemut integer,
    moismut integer,
    nbmutjour integer,
    nbmutannee integer,
    datemutpre date,
    l_idmutpre text[],
    datemutsui date,
    l_idmutsui text[],
    geomloc public.geometry
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_lot (
    idlot bigint,
    iddispo bigint,
    idmutation bigint,
    nolot text,
    sbati numeric,
    npprinc integer,
    coddep text
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_mutation (
    idmutation bigint,
    idmutinvar character varying,
    idopendata text,
    idnatmut integer,
    codservch text,
    refdoc text,
    datemut date,
    anneemut integer,
    moismut integer,
    coddep text,
    libnatmut text,
    nbartcgi bigint,
    l_artcgi text[],
    vefa boolean,
    valeurfonc numeric,
    nbdispo bigint,
    nblot numeric,
    nbcomm bigint,
    l_codinsee text[],
    nbsection bigint,
    l_section text[],
    nbpar bigint,
    l_idpar text[],
    nbparmut bigint,
    l_idparmut text[],
    nbsuf bigint,
    sterr numeric,
    l_dcnt numeric[],
    nbvolmut bigint,
    nblocmut bigint,
    l_idlocmut text[],
    nblocmai bigint,
    nblocapt bigint,
    nblocdep bigint,
    nblocact bigint,
    nbapt1pp bigint,
    nbapt2pp bigint,
    nbapt3pp bigint,
    nbapt4pp bigint,
    nbapt5pp bigint,
    nbmai1pp bigint,
    nbmai2pp bigint,
    nbmai3pp bigint,
    nbmai4pp bigint,
    nbmai5pp bigint,
    sbati numeric,
    sbatmai numeric,
    sbatapt numeric,
    sbatact numeric,
    sapt1pp numeric,
    sapt2pp numeric,
    sapt3pp numeric,
    sapt4pp numeric,
    sapt5pp numeric,
    smai1pp numeric,
    smai2pp numeric,
    smai3pp numeric,
    smai4pp numeric,
    smai5pp numeric,
    geomlocmut public.geometry,
    geomparmut public.geometry,
    geompar public.geometry,
    codtypbien text,
    libtypbien text
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_mutation_article_cgi (
    idmutation bigint,
    idartcgi integer,
    ordarticgi integer,
    coddep text
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_parcelle (
    idparcelle bigint,
    idpar text,
    coddep text,
    codcomm text,
    prefsect text,
    nosect text,
    noplan text
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_suf (
    idsuf bigint,
    iddispopar bigint,
    idmutation bigint,
    nosuf text,
    dcnt text,
    dsu numeric,
    l_codtypsuf text[],
    l_libtypsu text[],
    coddep text,
    datedsu date
);

CREATE TABLE dvf_plus_2025_2.dvf_plus_volume (
    idvolume bigint,
    iddispopar bigint,
    idmutation bigint,
    novol text,
    coddep text
);

-- Message de confirmation
SELECT 'Phase 2 Complete: Schema dvf_plus_2025_2 created with 12 tables' AS status;
