CREATE SCHEMA [core]
GO

CREATE SCHEMA [sale]
GO

CREATE SCHEMA [grandine]
GO

/*CORE*/
CREATE TABLE [core].[comune] (
    [codice_regione]                    integer,     
    [codice_unita]                      integer, 
    [codice_provincia]                  integer, 
    [progressivo_comune]                integer, 
    [codice_comune]                     integer PRIMARY KEY,
    [nome]                              NVARCHAR(255),   
    [codice_ripartizione_geografica]    integer,     
    [ripartizione_geografica]           NVARCHAR(50),    
    [denominazione_regione]             NVARCHAR(50),    
    [denominazione_unita]               NVARCHAR(50),    
    [tipologia_unita]                   integer,     
    [provincia_short]                   NVARCHAR(2),     
    [codice_catastale]                  NVARCHAR(8),     
    [codice_nuts3]                      NVARCHAR(10),
    [cap]                               NVARCHAR(5)
);
GO

CREATE TABLE [core].[persona_fisica] (
  [nome] nvarchar(255),
  [cf] nvarchar(16) PRIMARY KEY,
  [codice_comune] integer,
  [indirizzo] nvarchar(255),
  [sesso] nvarchar(1),
  [cell] nvarchar(16),
  [email] nvarchar(255),
  [pec] nvarchar(255),
  [data_di_nascita] DATE NULL, 
  [codice_comune_di_nascita] integer,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[caa_coldiretti] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [nome] nvarchar(255),
  [email] nvarchar(255),
  [cell] nvarchar(16),
  [codice_comune] integer,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[gruppo] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [nome] nvarchar(255),
  [referente_cf] nvarchar(16),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[ragione_sociale] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [nome] nvarchar(255),
  [responsabile_legale_cf] nvarchar(16),
  [CUAA] nvarchar(16),
  [piva] nvarchar(16),
  [gruppo_id] uniqueidentifier,
  [codice_comune] integer,
  [indirizzo] nvarchar(255),
  [IBAN] nvarchar(50),
  [caa_coldiretti_id] uniqueidentifier,
  [email] nvarchar(255),
  [pec] nvarchar(255),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[condifesa] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [nome] nvarchar(255),
  [email] nvarchar(255),
  [cell] nvarchar(16),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[compagnia] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [short_nome] nvarchar (100),
  [full_nome] nvarchar(255),
  [piva] nvarchar(16),
  [email] nvarchar(255),
  [pec] nvarchar(255),
  [cell] nvarchar(16),
  [indirizzo] nvarchar(255),
  [codice_comune] integer,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[intermediario] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [short_nome] nvarchar (100),
  [full_nome] nvarchar(255),
  [piva] nvarchar(16),
  [email] nvarchar(255),
  [pec] nvarchar(255),
  [cell] nvarchar(16),
  [indirizzo] nvarchar(255),
  [codice_comune] integer,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[ramo] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [ramo] nvarchar(255),
  [numero] integer,
  [nome] nvarchar(255),
  [dettaglio] nvarchar(255),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[relazione_rci] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [ramo_id] uniqueidentifier,
  [compagnia_id] uniqueidentifier,
  [intermediario_id] uniqueidentifier,
  [active] BIT DEFAULT (1),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[documento](
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [ramo_id] uniqueidentifier,
  [compagnia_id] uniqueidentifier,
  [intermediario_id] uniqueidentifier,
  [codice_ministeriale] nvarchar(4), 
  [nome] nvarchar(255),
  [sigla] nvarchar(50),
  [signed] BIT DEFAULT (0),
  [personale] BIT DEFAULT (0),
  [mandatory] BIT DEFAULT (0),
  [lifecycle_id] integer,
  [entity] BIT DEFAULT (0),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [core].[lifecycle] (
  [id] integer PRIMARY KEY,
  [sale_reference] nvarchar(20),
  [stato] nvarchar(50),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)

/*SALE*/
CREATE TABLE [sale].[preventivo] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [ragione_sociale_id] uniqueidentifier,
  [ramo_id] uniqueidentifier,
  [intermediario_id] uniqueidentifier,
  [compagnia_id] uniqueidentifier,
  [premio_lordo] decimal(12,2),
  [lifecycle_id] integer,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [sale].[produttore] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [persona_fisica_cf] nvarchar(16),
  [ramo_id] uniqueidentifier,
  [percentuale] decimal(5,2),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [sale].[documento_archivio](
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [ragione_sociale_id] uniqueidentifier,
  [documento_id] uniqueidentifier,
  [anno] integer,
  [file_path] nvarchar(500),
  [archivio] BIT DEFAULT (0),
  [signed] BIT DEFAULT (0),
  [sent] BIT DEFAULT (0),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [sale].[documento_archivio_preventivo] (
  [documento_archivio_id] uniqueidentifier NOT NULL,
  [preventivo_id] uniqueidentifier NOT NULL,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL


  CONSTRAINT [PK_documento_archivio_preventivo] PRIMARY KEY CLUSTERED 
        (
            [documento_archivio_id] ASC,
            [preventivo_id] ASC
        )
)
GO

CREATE TABLE [sale].[polizza](
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [numero] nvarchar(50),
  [ragione_sociale_id] uniqueidentifier,
  [ramo_id] uniqueidentifier,
  [intermediario_id] uniqueidentifier,
  [compagnia_id] uniqueidentifier,
  [premio_lordo] decimal(12,2),
  [lifecycle_id] integer,
  [produttore_id] uniqueidentifier,
  [preventivo_id] uniqueidentifier,
  [start_date] DATE,
  [end_date] DATE, 
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [sale].[documento_archivio_polizza] (
  [documento_archivio_id] uniqueidentifier NOT NULL,
  [polizza_id] uniqueidentifier NOT NULL,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL


  CONSTRAINT [PK_documento_archivio_polizza] PRIMARY KEY CLUSTERED 
        (
            [documento_archivio_id] ASC,
            [polizza_id] ASC
        )
)
GO

/*GRANDINE*/
CREATE TABLE [grandine].[preventivo] (
  [sale_preventivo_id] uniqueidentifier PRIMARY KEY,
  [piano_utilizzo_id] uniqueidentifier NOT NULL,
  [prezzo_id] uniqueidentifier,
  [contribuzione] BIT DEFAULT (1),
  [condifesa] BIT DEFAULT(1),
  [caa_coldiretti] BIT DEFAULT (1),

  [GR_AG_id] uniqueidentifier,
  [GR_NAG_id] uniqueidentifier,
  [VF_AG_id] uniqueidentifier,
  [VF_NAG_id] uniqueidentifier,
  [EP_AG_id] uniqueidentifier,
  [EP_NAG_id] uniqueidentifier,
  [EP_CAT_AG_id] uniqueidentifier,
  [EP_CAT_NAG_id] uniqueidentifier,
  [neve_AG_id] uniqueidentifier,
  [neve_NAG_id] uniqueidentifier,
  [alluvione_AG_id] uniqueidentifier,
  [gelo_brina_AG_id] uniqueidentifier,
  [siccita_AG_id] uniqueidentifier,
  [colpo_sole_vento_caldo_AG_id] uniqueidentifier,
  [colpo_sole_vento_caldo_NAG_id] uniqueidentifier,
  [colpo_sole_vento_caldo_CAT_AG_id] uniqueidentifier,
  [colpo_sole_vento_caldo_CAT_NAG_id] uniqueidentifier,
  [sbalzo_termico_onda_calore_AG_id] uniqueidentifier,
  [sbalzo_termico_onda_calore_NAG_id] uniqueidentifier,
  [sbalzo_termico_onda_calore_CAT_AG_id] uniqueidentifier,
  [sbalzo_termico_onda_calore_CAT_NAG_id] uniqueidentifier,

  [ag] decimal (4,2),
  [nag] decimal (4,2),
  [lordo] decimal (4,2),
  [resa_cliente] integer,
  [valore_assicurato] integer,
  [premio_lordo] decimal(12,2),
  [premio_netto] decimal (12,2),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME() NOT NULL,
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [grandine].[piano_utilizzo] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [ragione_sociale_id] uniqueidentifier,
  [condifesa_id] uniqueidentifier,
  [anno] integer,
  [tipo] nvarchar(50),
  [is_corrente] BIT DEFAULT (1),
  [codice_comune] integer,
  [prodotto_id] uniqueidentifier,
  [serra] BIT DEFAULT (0),
  [bio] BIT DEFAULT (0),
  [secondo_raccolto] BIT DEFAULT (0),
  [superficie] integer,
  [note] text,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [grandine].[piano_utilizzo_dettagliato] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [ragione_sociale_id] uniqueidentifier,
  [condifesa_id] uniqueidentifier,
  [anno] integer,
  [is_corrente] BIT DEFAULT (1),
  [codice_comune] integer,
  [prodotto_id] uniqueidentifier,
  [serra] BIT DEFAULT (0),
  [bio] BIT DEFAULT (0),
  [secondo_raccolto] BIT DEFAULT (0),
  [foglio] integer,
  [particella] integer,
  [superficie] integer,
  [data_semina_trapianto] DATE,
  [note] text,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [grandine].[partita] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [piano_utilizzo_dettagliato_id] uniqueidentifier,
  [numero] integer,
  [foglio] nvarchar(6),
  [particella] nvarchar(6),
  [superficie] integer,
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [grandine].[prodotto] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [condifesa_id] uniqueidentifier,
  [gruppo] nvarchar(100),
  [nome] nvarchar(255),
  [dettaglio] nvarchar(255),
  [codice_ministeriale] nvarchar(4),
  [codice_dettaglio_ministeriale] nvarchar(4),
  [codice_dettaglio_condifesa] nvarchar(5),
  [codice_prodotto] nvarchar(4),
  [dettaglio_avepa] nvarchar(100),
  [codice_avepa] integer,
  [codice_avepa_dettagliato] nvarchar(19),
  [codice_gis] nvarchar(10),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [grandine].[avepa] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [occupazione] nvarchar (255),
  [codice_occupazione] nvarchar(3),
  [destinazione] nvarchar (255),
  [codice_destinazione]	 nvarchar(3),
  [uso]	nvarchar(255),
  [codice_uso] nvarchar(3),
  [dettaglio]	nvarchar(255),
  [codice_dettaglio] nvarchar(3),
  [codice_ministeriale] nvarchar(3),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)

CREATE TABLE [grandine].[prezzi] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [anno] integer,
  [condifesa_id] uniqueidentifier,
  [prodotto_id] uniqueidentifier,
  [area] nvarchar(50),
  [sv] decimal(10,2),
  [resa_max] decimal(10,2),
  [sv_bio] decimal(10,2),
  [fascia] nvarchar(1),
  [valore] decimal(10,2),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [grandine].[tassi] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [anno] integer,
  [intermediario_id] uniqueidentifier,
  [compagnia_id] uniqueidentifier,
  [codice_comune] integer,
  [codice_ministeriale] nvarchar(4),
  [tabella_conversione] nvarchar(2),
  [tipo] nvarchar(50),
  [garanzia] nvarchar (50),
  [fr] integer,
  [tasso] nvarchar (3),
  [valore] DECIMAL (4,2),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME(),
  [updated_at] datetime2 NULL
)
GO

CREATE TABLE [grandine].[socio](
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [ragione_sociale_id] uniqueidentifier,
  [condifesa_id] uniqueidentifier,
  [codice_socio] nvarchar(50)
)
GO

CREATE TABLE [grandine].[polizza] (
  [id] uniqueidentifier PRIMARY KEY DEFAULT NEWID(),
  [sale_polizza_id] uniqueidentifier NOT NULL,
  [partita_id] uniqueidentifier NOT NULL,
  [ag] BIT DEFAULT (1),
  [created_at] datetime2 DEFAULT SYSUTCDATETIME() NOT NULL,
  [updated_at] datetime2 NULL
)
GO

/*CORE*/
ALTER TABLE [core].[persona_fisica] ADD FOREIGN KEY ([codice_comune]) REFERENCES [core].[comune] (codice_comune)
GO

ALTER TABLE [core].[caa_coldiretti] ADD FOREIGN KEY ([codice_comune]) REFERENCES [core].[comune] (codice_comune)
GO

ALTER TABLE [core].[gruppo] ADD FOREIGN KEY ([referente_cf]) REFERENCES [core].[persona_fisica] ([cf])
GO

ALTER TABLE [core].[ragione_sociale] ADD FOREIGN KEY ([responsabile_legale_cf]) REFERENCES [core].[persona_fisica] ([cf])
GO

ALTER TABLE [core].[ragione_sociale] ADD FOREIGN KEY ([gruppo_id]) REFERENCES [core].[gruppo] ([id])
GO

ALTER TABLE [core].[ragione_sociale] ADD FOREIGN KEY ([codice_comune]) REFERENCES [core].[comune] (codice_comune)
GO

ALTER TABLE [core].[ragione_sociale] ADD FOREIGN KEY ([caa_coldiretti_id]) REFERENCES [core].[caa_coldiretti] ([id])
GO

ALTER TABLE [core].[intermediario] ADD FOREIGN KEY ([codice_comune]) REFERENCES [core].[comune] ([codice_comune])
GO

ALTER TABLE [core].[compagnia] ADD FOREIGN KEY ([codice_comune]) REFERENCES [core].[comune] ([codice_comune])
GO

ALTER TABLE [core].[relazione_rci] ADD FOREIGN KEY ([ramo_id]) REFERENCES [core].[ramo] ([id])
GO

ALTER TABLE [core].[relazione_rci] ADD FOREIGN KEY ([intermediario_id]) REFERENCES [core].[intermediario] ([id])
GO

ALTER TABLE [core].[relazione_rci] ADD FOREIGN KEY ([compagnia_id]) REFERENCES [core].[compagnia] ([id])
GO

ALTER TABLE [core].[documento] ADD FOREIGN KEY ([ramo_id]) REFERENCES [core].[ramo] ([id])
GO

ALTER TABLE [core].[documento] ADD FOREIGN KEY ([intermediario_id]) REFERENCES [core].[intermediario] ([id])
GO

ALTER TABLE [core].[documento] ADD FOREIGN KEY ([compagnia_id]) REFERENCES [core].[compagnia] ([id])
GO

ALTER TABLE [core].[documento] ADD FOREIGN KEY ([lifecycle_id]) REFERENCES [core].[lifecycle] ([id])
GO


/*SALE*/
ALTER TABLE [sale].[preventivo] ADD FOREIGN KEY ([intermediario_id]) REFERENCES [core].[intermediario] ([id])
GO

ALTER TABLE [sale].[preventivo] ADD FOREIGN KEY ([compagnia_id]) REFERENCES [core].[compagnia] ([id])
GO

ALTER TABLE [sale].[preventivo] ADD FOREIGN KEY ([ragione_sociale_id]) REFERENCES [core].[ragione_sociale] ([id])
GO

ALTER TABLE [sale].[preventivo] ADD FOREIGN KEY ([ramo_id]) REFERENCES [core].[ramo] ([id])
GO

ALTER TABLE [sale].[preventivo] ADD FOREIGN KEY ([lifecycle_id]) REFERENCES [core].[lifecycle] ([id])
GO

ALTER TABLE [sale].[polizza] ADD FOREIGN KEY ([intermediario_id]) REFERENCES [core].[intermediario] ([id])
GO

ALTER TABLE [sale].[polizza] ADD FOREIGN KEY ([compagnia_id]) REFERENCES [core].[compagnia] ([id])
GO

ALTER TABLE [sale].[polizza] ADD FOREIGN KEY ([ragione_sociale_id]) REFERENCES [core].[ragione_sociale] ([id])
GO

ALTER TABLE [sale].[polizza] ADD FOREIGN KEY ([ramo_id]) REFERENCES [core].[ramo] ([id])
GO

ALTER TABLE [sale].[polizza] ADD FOREIGN KEY ([lifecycle_id]) REFERENCES [core].[lifecycle] ([id])
GO

ALTER TABLE [sale].[polizza] ADD FOREIGN KEY ([produttore_id]) REFERENCES [sale].[produttore] ([id])
GO

ALTER TABLE [sale].[polizza] ADD FOREIGN KEY ([preventivo_id]) REFERENCES [sale].[preventivo] ([id])
GO


ALTER TABLE [sale].[produttore] ADD FOREIGN KEY ([ramo_id]) REFERENCES [core].[ramo] ([id])
GO

ALTER TABLE [sale].[produttore] ADD FOREIGN KEY ([persona_fisica_cf]) REFERENCES [core].[persona_fisica] ([cf])
GO

ALTER TABLE [sale].[documento_archivio] ADD FOREIGN KEY ([ragione_sociale_id]) REFERENCES [core].[ragione_sociale] ([id])
GO

ALTER TABLE [sale].[documento_archivio] ADD FOREIGN KEY ([documento_id]) REFERENCES [core].[documento] ([id])
GO

ALTER TABLE [sale].[documento_archivio_preventivo] ADD FOREIGN KEY ([preventivo_id]) REFERENCES [sale].[preventivo] ([id])
GO

ALTER TABLE [sale].[documento_archivio_preventivo] ADD FOREIGN KEY ([documento_archivio_id]) REFERENCES [sale].[documento_archivio] ([id])
GO

ALTER TABLE [sale].[documento_archivio_polizza] ADD FOREIGN KEY ([polizza_id]) REFERENCES [sale].[polizza] ([id])
GO

ALTER TABLE [sale].[documento_archivio_polizza] ADD FOREIGN KEY ([documento_archivio_id]) REFERENCES [sale].[documento_archivio] ([id])
GO

/*GRANDINE*/
ALTER TABLE [grandine].[piano_utilizzo] ADD FOREIGN KEY ([ragione_sociale_id]) REFERENCES [core].[ragione_sociale] ([id])
GO

ALTER TABLE [grandine].[piano_utilizzo] ADD FOREIGN KEY ([condifesa_id]) REFERENCES [core].[condifesa] ([id])
GO

ALTER TABLE [grandine].[piano_utilizzo] ADD FOREIGN KEY ([codice_comune]) REFERENCES [core].[comune] (codice_comune)
GO

ALTER TABLE [grandine].[piano_utilizzo] ADD FOREIGN KEY ([prodotto_id]) REFERENCES [grandine].[prodotto] ([id])
GO

ALTER TABLE [grandine].[prezzi] ADD FOREIGN KEY ([condifesa_id]) REFERENCES [core].[condifesa] ([id])
GO

ALTER TABLE [grandine].[prezzi] ADD FOREIGN KEY ([prodotto_id]) REFERENCES [grandine].[prodotto] ([id])
GO

ALTER TABLE [grandine].[prodotto] ADD FOREIGN KEY ([condifesa_id]) REFERENCES [core].[condifesa] ([id])
GO

ALTER TABLE [grandine].[tassi] ADD FOREIGN KEY ([intermediario_id]) REFERENCES [core].[intermediario] ([id])
GO  

ALTER TABLE [grandine].[tassi] ADD FOREIGN KEY ([compagnia_id]) REFERENCES [core].[compagnia] ([id])
GO

ALTER TABLE [grandine].[tassi] ADD FOREIGN KEY ([codice_comune]) REFERENCES [core].[comune] ([codice_comune])
GO

ALTER TABLE [grandine].[preventivo] ADD FOREIGN KEY ([sale_preventivo_id]) REFERENCES [sale].[preventivo] (id)
GO

ALTER TABLE [grandine].[preventivo] ADD FOREIGN KEY ([piano_utilizzo_id]) REFERENCES [grandine].[piano_utilizzo] (id)
GO

ALTER TABLE [grandine].[preventivo] ADD FOREIGN KEY ([prezzo_id]) REFERENCES [grandine].[prezzi] (id)
GO

ALTER TABLE [grandine].[polizza] ADD FOREIGN KEY ([sale_polizza_id]) REFERENCES [sale].[polizza] (id)
GO

ALTER TABLE [grandine].[polizza] ADD FOREIGN KEY ([partita_id]) REFERENCES [grandine].[partita] (id)
GO

ALTER TABLE [grandine].[socio] ADD FOREIGN KEY ([ragione_sociale_id]) REFERENCES [core].[ragione_sociale] (id)
GO

ALTER TABLE [grandine].[socio] ADD FOREIGN KEY ([condifesa_id]) REFERENCES [core].[condifesa] (id)
GO

ALTER TABLE [grandine].[piano_utilizzo_dettagliato] ADD FOREIGN KEY ([ragione_sociale_id]) REFERENCES [core].[ragione_sociale] ([id])
GO

ALTER TABLE [grandine].[piano_utilizzo_dettagliato] ADD FOREIGN KEY ([condifesa_id]) REFERENCES [core].[condifesa] ([id])
GO

ALTER TABLE [grandine].[piano_utilizzo_dettagliato] ADD FOREIGN KEY ([codice_comune]) REFERENCES [core].[comune] (codice_comune)
GO

ALTER TABLE [grandine].[piano_utilizzo_dettagliato] ADD FOREIGN KEY ([prodotto_id]) REFERENCES [grandine].[prodotto] ([id])
GO

ALTER TABLE [grandine].[partita] ADD FOREIGN KEY ([piano_utilizzo_dettagliato_id]) REFERENCES [grandine].[piano_utilizzo_dettagliato] ([id])
GO

/* STORED PROCEDURE */

CREATE OR ALTER PROCEDURE grandine.sp_confronto_piano_utilizzo
    @ragione_sociale_id NVARCHAR(36)
AS
BEGIN
    SET NOCOUNT ON;

    WITH PuSummary AS (
            SELECT 
                condifesa_id, anno, codice_comune, prodotto_id, 
                serra, bio, secondo_raccolto, 
                SUM(superficie) as tot_sup
            FROM grandine.piano_utilizzo
            WHERE ragione_sociale_id = @ragione_sociale_id
            GROUP BY condifesa_id, anno, codice_comune, prodotto_id, serra, bio, secondo_raccolto
        ),
        -- 2. Summarize Dettaglio (PUD)
        PudSummary AS (
            SELECT 
                condifesa_id, anno, codice_comune, prodotto_id, 
                serra, bio, secondo_raccolto, 
                SUM(superficie) as tot_sup
            FROM grandine.piano_utilizzo_dettagliato
            WHERE ragione_sociale_id = @ragione_sociale_id
            GROUP BY condifesa_id, anno, codice_comune, prodotto_id, serra, bio, secondo_raccolto
        ),
        -- 3. Combine Data (The "Raw" Comparison)
        Combined AS (
            SELECT
                COALESCE(a.condifesa_id, b.condifesa_id) as condifesa_id,
                COALESCE(a.anno, b.anno) as anno,
                COALESCE(a.codice_comune, b.codice_comune) as codice_comune,
                COALESCE(a.prodotto_id, b.prodotto_id) as prodotto_id,
                COALESCE(a.serra, b.serra) as serra,
                COALESCE(a.bio, b.bio) as bio,
                COALESCE(a.secondo_raccolto, b.secondo_raccolto) as secondo_raccolto,
                ISNULL(a.tot_sup, 0) as sup_riepilogo,
                ISNULL(b.tot_sup, 0) as sup_dettaglio
            FROM PuSummary a
            FULL OUTER JOIN PudSummary b
                ON a.condifesa_id = b.condifesa_id
               AND a.anno = b.anno
               AND a.codice_comune = b.codice_comune
               AND a.prodotto_id = b.prodotto_id
               AND a.serra = b.serra
               AND a.bio = b.bio
               AND a.secondo_raccolto = b.secondo_raccolto
        )
        -- 4. Final Select with Joins to get Names
        SELECT 
            res.*,
            ABS(res.sup_riepilogo - res.sup_dettaglio) as diff,
        
            -- Joined Names
            c.nome as condifesa_nome,
            com.nome as comune_nome,
            p.nome as prodotto_nome,
            p.dettaglio as prodotto_dettaglio
        
        FROM Combined res
        LEFT JOIN core.condifesa c ON res.condifesa_id = c.id
        LEFT JOIN core.comune com ON res.codice_comune = com.codice_comune
        LEFT JOIN grandine.prodotto p ON res.prodotto_id = p.id;
END;
GO