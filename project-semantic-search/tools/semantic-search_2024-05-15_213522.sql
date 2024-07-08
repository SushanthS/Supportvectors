--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.2

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
    processed_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    text_extract_time_ms bigint,
    chunk_time_ms bigint,
    encode_time_ms bigint,
    file_hash text,
    faiss_indexed boolean DEFAULT false,
    chunked boolean DEFAULT false,
    vectorized boolean DEFAULT false,
    extracted_text text
);


ALTER TABLE "semantic-search".corpus OWNER TO postgres;

--
-- Name: corpus_id_seq; Type: SEQUENCE; Schema: semantic-search; Owner: postgres
--

ALTER TABLE "semantic-search".corpus ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "semantic-search".corpus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: corpus_metadata_view; Type: VIEW; Schema: semantic-search; Owner: postgres
--

CREATE VIEW "semantic-search".corpus_metadata_view AS
 SELECT id,
    filename,
    path,
    processed_time,
    text_extract_time_ms,
    chunk_time_ms AS chunk_time_sec,
    encode_time_ms AS encode_time_sec,
    file_hash,
    chunked,
    vectorized,
    faiss_indexed
   FROM "semantic-search".corpus;


ALTER VIEW "semantic-search".corpus_metadata_view OWNER TO postgres;

--
-- Name: corpus corpus_pkey; Type: CONSTRAINT; Schema: semantic-search; Owner: postgres
--

ALTER TABLE ONLY "semantic-search".corpus
    ADD CONSTRAINT corpus_pkey PRIMARY KEY (id);


CREATE SCHEMA "semantic-chunks";


ALTER SCHEMA "semantic-chunks" OWNER TO postgres;
--
-- PostgreSQL database dump complete
--
