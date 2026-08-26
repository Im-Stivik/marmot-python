#!/bin/sh
set -eu

export HADOOP_HOME=/opt/hadoop-3.2.0
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-${HADOOP_HOME}/etc/hadoop}"
export HADOOP_CLASSPATH="${HADOOP_HOME}/share/hadoop/tools/lib/aws-java-sdk-bundle-1.11.375.jar:${HADOOP_HOME}/share/hadoop/tools/lib/hadoop-aws-3.2.0.jar"
export JAVA_HOME=/usr/local/openjdk-8
export METASTORE_DB_HOSTNAME="${METASTORE_DB_HOSTNAME:-postgres}"
export METASTORE_DB_PORT="${METASTORE_DB_PORT:-5432}"
export HIVE_HOME=/opt/apache-hive-metastore-3.0.0-bin

# Make sure the Postgres JDBC driver is on the metastore classpath.
PG_JAR="${HIVE_HOME}/lib/postgresql-42.7.4.jar"
if [ ! -f "${PG_JAR}" ]; then
  echo "ERROR: ${PG_JAR} is missing (mount docker/hive/lib/postgresql-42.7.4.jar)"
  exit 1
fi
export HADOOP_CLASSPATH="${HADOOP_CLASSPATH}:${PG_JAR}"
export AUX_CLASSPATH="${PG_JAR}"
export HIVE_AUX_JARS_PATH="${PG_JAR}"

SCHEMA_TOOL=/opt/apache-hive-metastore-3.0.0-bin/bin/schematool

echo "Waiting for database on ${METASTORE_DB_HOSTNAME}:${METASTORE_DB_PORT} ..."
while ! nc -z "${METASTORE_DB_HOSTNAME}" "${METASTORE_DB_PORT}"; do
  sleep 1
done
echo "Database on ${METASTORE_DB_HOSTNAME}:${METASTORE_DB_PORT} started"

if "${SCHEMA_TOOL}" -info -dbType postgres >/dev/null 2>&1; then
  echo "Hive Metastore schema already present, skipping init"
else
  echo "Initializing Hive Metastore schema on Postgres..."
  "${SCHEMA_TOOL}" -initSchema -dbType postgres || \
    echo "Schema init returned non-zero (often already initialized), continuing..."
fi

echo "Starting Metastore Server on 0.0.0.0:9083"
exec /opt/apache-hive-metastore-3.0.0-bin/bin/start-metastore -p 9083
