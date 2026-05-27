import numpy as np
import pandas as pd
from core.agent import ArcaAgent, EstadoAgente


class ResultsAnalyzer:
    def __init__(self, experimento: dict):
        self.exp = experimento
        self.resultados = experimento.get("resultados", {})
        self.snapshots = self.resultados.get("snapshots", [])
        self.agentes = self.resultados.get("agentes", [])

    def resumen_ejecutivo(self) -> dict:
        if not self.snapshots:
            return {}

        final = self.snapshots[-1]
        conteos = final.get("conteos", {})
        total = final.get("total_agentes", 1)

        paso_adopcion_masiva = None
        for i, snap in enumerate(self.snapshots):
            if snap.get("tasa_adopcion", 0) >= 0.5:
                paso_adopcion_masiva = i
                break

        return {
            "tasa_adopcion_final": round(final.get("tasa_adopcion", 0), 4),
            "interes_medio_final": round(final.get("interes_medio", 0), 4),
            "pct_adoptados": round(conteos.get("adoptado", 0) / total, 4),
            "pct_rechazados": round(conteos.get("rechazado", 0) / total, 4),
            "pct_interesados": round(conteos.get("interesado", 0) / total, 4),
            "pct_escepticos": round(conteos.get("esceptico", 0) / total, 4),
            "pct_neutros": round(conteos.get("neutral", 0) / total, 4),
            "paso_adopcion_masiva": paso_adopcion_masiva,
            "total_pasos": len(self.snapshots),
            "total_agentes": total,
            "conteos_finales": conteos,
        }

    def segmentar_por_perfil(self) -> dict:
        if not self.agentes:
            return {}

        df = pd.DataFrame(self.agentes)
        resultado = {}

        for col in ["nivel_educativo", "ciudad", "situacion_laboral", "genero"]:
            if col in df.columns:
                resultado[col] = (
                    df.groupby(col)["estado"]
                    .value_counts(normalize=True)
                    .unstack(fill_value=0)
                    .round(3)
                    .to_dict()
                )

        if "ingreso_mensual" in df.columns:
            df["segmento_ingreso"] = pd.cut(
                df["ingreso_mensual"],
                bins=[0, 600_000, 1_000_000, 1_800_000, 3_100_000],
                labels=["Bajo", "Medio-Bajo", "Medio-Alto", "Alto"],
            )
            resultado["segmento_ingreso"] = (
                df.groupby("segmento_ingreso")["estado"]
                .value_counts(normalize=True)
                .unstack(fill_value=0)
                .round(3)
                .to_dict()
            )

        return resultado

    def curva_difusion(self) -> dict:
        if not self.snapshots:
            return {}

        pasos = [s["step"] for s in self.snapshots]
        adoptados = [s["conteos"].get("adoptado", 0) for s in self.snapshots]
        interesados = [s["conteos"].get("interesado", 0) for s in self.snapshots]
        escepticos = [s["conteos"].get("esceptico", 0) for s in self.snapshots]
        rechazados = [s["conteos"].get("rechazado", 0) for s in self.snapshots]
        neutros = [s["conteos"].get("neutral", 0) for s in self.snapshots]
        interes_medio = [s.get("interes_medio", 0) for s in self.snapshots]

        return {
            "pasos": pasos,
            "adoptados": adoptados,
            "interesados": interesados,
            "escepticos": escepticos,
            "rechazados": rechazados,
            "neutros": neutros,
            "interes_medio": interes_medio,
        }

    def factores_criticos(self) -> list[dict]:
        if not self.agentes:
            return []

        df = pd.DataFrame(self.agentes)
        df["adoptado"] = df["estado"] == "adoptado"
        factores = []

        atributos_numericos = [
            "apertura_cambio", "aversion_riesgo", "influenciabilidad",
            "orientacion_logro", "disposicion_pago", "sensibilidad_precio",
        ]
        for col in atributos_numericos:
            if col not in df.columns:
                continue
            media_adoptados = df[df["adoptado"]][col].mean()
            media_no = df[~df["adoptado"]][col].mean()
            diff = media_adoptados - media_no
            factores.append({
                "factor": col,
                "media_adoptados": round(media_adoptados, 3),
                "media_no_adoptados": round(media_no, 3),
                "diferencia": round(diff, 3),
                "importancia": round(abs(diff), 3),
            })

        return sorted(factores, key=lambda x: x["importancia"], reverse=True)

    def get_serie_tiempo_df(self) -> pd.DataFrame:
        serie = self.resultados.get("serie_tiempo", {})
        if not serie:
            return pd.DataFrame()
        return pd.DataFrame(serie)

    def recomendaciones(self) -> list[str]:
        resumen = self.resumen_ejecutivo()
        factores = self.factores_criticos()
        recomendaciones = []

        tasa = resumen.get("tasa_adopcion_final", 0)
        if tasa < 0.1:
            recomendaciones.append("Tasa de adopción muy baja. Revisar precio, modalidad o propuesta de valor.")
        elif tasa < 0.25:
            recomendaciones.append("Adopción por debajo de expectativas. Considerar ajustes en financiamiento o marketing.")
        elif tasa >= 0.5:
            recomendaciones.append("Alta adopción. El programa tiene buena receptividad en este segmento.")

        if factores:
            top = factores[0]
            if top["diferencia"] > 0.15:
                recomendaciones.append(
                    f"El factor '{top['factor']}' diferencia fuertemente a los adoptantes. "
                    "Enfocar campañas en perfiles con alto valor en este atributo."
                )

        pct_rechazados = resumen.get("pct_rechazados", 0)
        if pct_rechazados > 0.3:
            recomendaciones.append(
                "Alto porcentaje de rechazo. Investigar barreras específicas (precio, modalidad, confianza)."
            )

        return recomendaciones
