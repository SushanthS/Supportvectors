--
-- PostgreSQL database dump
--

-- Dumped from database version 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.11 (Ubuntu 14.11-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: semantic-chunks; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "semantic-chunks";


ALTER SCHEMA "semantic-chunks" OWNER TO postgres;

--
-- Name: semantic-search; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "semantic-search";


ALTER SCHEMA "semantic-search" OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: corpus; Type: TABLE; Schema: semantic-search; Owner: postgres
--

CREATE TABLE "semantic-search".corpus (
    id bigint NOT NULL,
    filename text,
    path text,
    process_time timestamp with time zone,
    text_extract_time_ms bigint,
    chunk_time_sec bigint,
    encode_time_sec bigint,
    file_hash text
);


ALTER TABLE "semantic-search".corpus OWNER TO postgres;

--
-- Name: corpus_id_seq; Type: SEQUENCE; Schema: semantic-search; Owner: postgres
--

CREATE SEQUENCE "semantic-search".corpus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "semantic-search".corpus_id_seq OWNER TO postgres;

--
-- Name: corpus_id_seq; Type: SEQUENCE OWNED BY; Schema: semantic-search; Owner: postgres
--

ALTER SEQUENCE "semantic-search".corpus_id_seq OWNED BY "semantic-search".corpus.id;


--
-- Name: corpus id; Type: DEFAULT; Schema: semantic-search; Owner: postgres
--

ALTER TABLE ONLY "semantic-search".corpus ALTER COLUMN id SET DEFAULT nextval('"semantic-search".corpus_id_seq'::regclass);


--
-- Data for Name: corpus; Type: TABLE DATA; Schema: semantic-search; Owner: postgres
--

COPY "semantic-search".corpus (id, filename, path, process_time, text_extract_time_ms, chunk_time_sec, encode_time_sec, file_hash) FROM stdin;
\.


--
-- Name: corpus_id_seq; Type: SEQUENCE SET; Schema: semantic-search; Owner: postgres
--

SELECT pg_catalog.setval('"semantic-search".corpus_id_seq', 1, false);


--
-- Name: corpus corpus_pkey; Type: CONSTRAINT; Schema: semantic-search; Owner: postgres
--

ALTER TABLE ONLY "semantic-search".corpus
    ADD CONSTRAINT corpus_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

