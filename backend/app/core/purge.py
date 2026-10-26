"""Borrado definitivo desde la consola (empresas y cuentas): recorre las llaves foráneas del modelo.

Las filas que dependen obligatoriamente de lo que se borra (llave NOT NULL) se borran primero, en cascada; las que
solo lo mencionan (llave que admite NULL, como un movimiento de @pples que nombra la empresa) se conservan y quedan
desvinculadas. Así no se rompen la contabilidad ni el rastro de auditoría.
"""
from __future__ import annotations

from sqlalchemy import Table, delete, select, update
from sqlalchemy.orm import Session

from app.core.database import Base

MAX_DEPTH = 12


def _children(table: Table):
    """(tabla hija, columna que apunta a `table`) para cada llave foránea hacia ella."""
    for t in Base.metadata.sorted_tables:
        for fk in t.foreign_keys:
            if fk.column.table is table:
                yield t, fk.parent


def purge(db: Session, table: Table, ids: list, depth: int = 0) -> int:
    """Borra las filas `ids` de `table` y lo que depende de ellas. Devuelve cuántas filas se borraron en total."""
    ids = [i for i in ids if i is not None]
    if not ids or depth > MAX_DEPTH:
        return 0
    removed = 0
    pk = list(table.primary_key.columns)[0]
    for child, col in list(_children(table)):
        if child is table:  # referencia a sí misma (p. ej. «versión anterior»): se desvincula
            if col.nullable:
                db.execute(update(child).where(col.in_(ids)).values({col.name: None}))
            continue
        if col.nullable:
            db.execute(update(child).where(col.in_(ids)).values({col.name: None}))
            continue
        child_pk = list(child.primary_key.columns)
        if len(child_pk) == 1:
            child_ids = [r[0] for r in db.execute(select(child_pk[0]).where(col.in_(ids))).all()]
            removed += purge(db, child, child_ids, depth + 1)
        else:
            removed += db.execute(delete(child).where(col.in_(ids))).rowcount or 0
    removed += db.execute(delete(table).where(pk.in_(ids))).rowcount or 0
    return removed
