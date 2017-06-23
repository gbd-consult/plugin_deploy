drop table if exists plugins;
create table plugins (
      id integer primary key autoincrement,
      name text not null,
      version text not null,
      description text not null,
      qgis_minimum_version text not null,
      qgis_maximum_version text not null,
      homepage text not null,
      file_name text not null,
      author_name text not null,
      download_url text not null,
      uploaded_by text not null,
      create_date text not null,
      update_date text not null,
      experimental text not null
);
