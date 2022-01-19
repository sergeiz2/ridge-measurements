CREATE TABLE "irrad_batch" (
  "id" SERIAL PRIMARY KEY NOT NULL,
  "name" varchar,
  "date" timestamptz NOT NULL DEFAULT (now()),
  "angle" real NOT NULL,
  "tgt_fluence" "double precision" NOT NULL,
  "duration" real NOT NULL,
  "base_press" "double precision" NOT NULL,
  "start_curr" real NOT NULL,
  "start_flux" "generated always as (end_curr * cos(angle) * 5006.1731) stored" NOT NULL,
  "op_press" "double precision" NOT NULL,
  "bm_volt" real NOT NULL,
  "cath_curr" real NOT NULL,
  "disch_curr" real NOT NULL,
  "disch_volt" real NOT NULL,
  "beam_curr" real NOT NULL,
  "acc_curr" real NOT NULL,
  "acc_volt" real NOT NULL,
  "nutr_emiss" real NOT NULL DEFAULT 0,
  "fil_curr" real NOT NULL DEFAULT 0,
  "end_curr" real NOT NULL,
  "avg_fluence" "double precision" NOT NULL,
  "misc" jsonb
);

CREATE TABLE "sample" (
  "edi_sample_id" SERIAL PRIMARY KEY NOT NULL,
  "name" varchar,
  "dimensions" varchar,
  "composition" varchar,
  "mfr_sample_id" varchar,
  "batch" integer
);

CREATE TABLE "image" (
  "id" SERIAL NOT NULL,
  "radial_loc" varchar,
  "linear_loc" varchar,
  "thread_loc" varchar,
  "sample_id" integer,
  "img_data" varbinary,
  "path" varchar,
  "avg_wavelength" float,
  PRIMARY KEY ("id", "radial_loc", "linear_loc", "thread_loc", "sample_id")
);

CREATE TABLE "line_measurement" (
  "id" SERIAL NOT NULL,
  "image_id" integer,
  "radial_loc" varchar,
  "linear_loc" varchar,
  "thread_loc" varchar,
  "sample_id" integer,
  "meas_by" varchar NOT NULL DEFAULT 'user',
  "length" float NOT NULL DEFAULT 0,
  "intercepts" integer NOT NULL,
  "unit" varchar NOT NULL DEFAULT 'nm',
  PRIMARY KEY ("id", "image_id", "radial_loc", "linear_loc", "thread_loc", "sample_id")
);

ALTER TABLE "sample" ADD FOREIGN KEY ("batch") REFERENCES "irrad_batch" ("id");

ALTER TABLE "sample" ADD FOREIGN KEY ("edi_sample_id") REFERENCES "image" ("sample_id");

ALTER TABLE "line_measurement" ADD FOREIGN KEY ("image_id", "radial_loc", "linear_loc", "thread_loc", "sample_id") REFERENCES "image" ("id", "radial_loc", "linear_loc", "thread_loc", "sample_id");


COMMENT ON COLUMN "irrad_batch"."name" IS 'Name of this batch';

COMMENT ON COLUMN "irrad_batch"."date" IS 'When this batch was irradiated';

COMMENT ON COLUMN "irrad_batch"."angle" IS 'radians';

COMMENT ON COLUMN "irrad_batch"."tgt_fluence" IS 'Target fluence (tera-ions per cm squared, 1E+12)';

COMMENT ON COLUMN "irrad_batch"."duration" IS 'Irradiation time, calculated from target fluence (sec)';

COMMENT ON COLUMN "irrad_batch"."base_press" IS 'Lowest chamber pressure achieved before turning on DIS gas flow (Torr)';

COMMENT ON COLUMN "irrad_batch"."start_curr" IS 'Ion beam curent measured by current plate before irradiation (mA)';

COMMENT ON COLUMN "irrad_batch"."start_flux" IS 'Flux calculated from start_curr (tera-ions per cm squared per second, 1E+12)';

COMMENT ON COLUMN "irrad_batch"."op_press" IS 'Operating pressure, after gas flow and ion source are turned on (Torr)';

COMMENT ON COLUMN "irrad_batch"."bm_volt" IS 'Beam voltage and electron energy are the same value. (V, eV, respectively)';

COMMENT ON COLUMN "irrad_batch"."cath_curr" IS 'Cathode filament current on ion source (A)';

COMMENT ON COLUMN "irrad_batch"."disch_curr" IS 'Discharge current (A)';

COMMENT ON COLUMN "irrad_batch"."disch_volt" IS 'Discharge voltage (V)';

COMMENT ON COLUMN "irrad_batch"."beam_curr" IS 'Beam current (mA)';

COMMENT ON COLUMN "irrad_batch"."acc_curr" IS 'Accelerator current (mA)';

COMMENT ON COLUMN "irrad_batch"."acc_volt" IS 'Accelerator voltage (V)';

COMMENT ON COLUMN "irrad_batch"."nutr_emiss" IS 'Neutralizer emission (mA)';

COMMENT ON COLUMN "irrad_batch"."fil_curr" IS 'Filament current (mA)';

COMMENT ON COLUMN "irrad_batch"."end_curr" IS 'Current measured after irradiation (mA)';

COMMENT ON COLUMN "irrad_batch"."avg_fluence" IS 'Experimental fluence, calculated from average current and angle (tera-ions per cm squared, 1E+12)';

COMMENT ON COLUMN "irrad_batch"."misc" IS 'Notes and miscellaneous other values';
