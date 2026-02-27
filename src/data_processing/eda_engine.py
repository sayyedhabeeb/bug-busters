"""
EDA Engine
----------
Full Exploratory Data Analysis with visualizations.

Charts saved to:  outputs/reports/eda/
JSON summary:     outputs/reports/eda/eda_summary.json
Markdown report:  outputs/reports/eda/EDA_REPORT.md

Run:
    python main.py --eda
    python src/data_processing/eda_engine.py
"""

import json
import logging
import warnings
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib
matplotlib.use("Agg")          # headless — no display needed
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

# ── colour palette & style constants ──────────────────────────────────────────
_PAL   = ["#c0392b","#2471a3","#1e8449","#d35400","#7d3c98",
          "#1a5276","#b7950b","#117a65","#784212","#4d5656","#6e2f6e","#1a6b4a"]
_BG    = "#f5f2eb"
_INK   = "#1a1814"
_MUTED = "#8c8679"
_GRID  = "#d4cfc4"

# tokens to ignore when counting skill frequency (too short / too generic)
_NOISE = {"r","go","less","sem","fea","js","ai","ml","ds","css","c","c#","c++"}


def _apply_style() -> None:
    plt.rcParams.update({
        "figure.facecolor":  _BG,
        "axes.facecolor":    _BG,
        "axes.edgecolor":    _GRID,
        "axes.labelcolor":   _INK,
        "axes.titlecolor":   _INK,
        "axes.titlesize":    12,
        "axes.titleweight":  "bold",
        "axes.titlepad":     10,
        "axes.grid":         True,
        "grid.color":        _GRID,
        "grid.linewidth":    0.6,
        "xtick.color":       _MUTED,
        "ytick.color":       _MUTED,
        "text.color":        _INK,
        "font.family":       "monospace",
        "savefig.facecolor": _BG,
        "savefig.dpi":       150,
        "savefig.bbox":      "tight",
    })


def _save(fig: plt.Figure, out_dir: Path, filename: str) -> None:
    path = out_dir / filename
    fig.savefig(path)
    plt.close(fig)
    logger.info("    saved → %s", filename)


# ══════════════════════════════════════════════════════════════════════════════
class EDAEngine:
    """
    Full EDA engine — replaces the original stub.
    Generates 21 charts + JSON summary + Markdown report.
    Fully compatible with  python main.py --eda
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.root       = project_root or Path(__file__).resolve().parents[2]
        self.interim    = self.root / "data" / "interim"
        self.feat_dir   = self.root / "data" / "processed" / "features"
        self.out_dir    = self.root / "outputs" / "reports" / "eda"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        # keep legacy path working (main.py writes to outputs/reports)
        legacy = self.root / "outputs" / "reports"
        legacy.mkdir(parents=True, exist_ok=True)
        _apply_style()

    # ── public entry ──────────────────────────────────────────────────────────
    def run_full_eda(self) -> Dict[str, Any]:
        """Run all EDA steps.  Called by  python main.py --eda"""
        logger.info("=" * 56)
        logger.info("  EDA ENGINE — starting")
        logger.info("=" * 56)

        data = self._load()
        if data is None:
            return {"status": "error", "message": "interim data not found"}

        resumes, jobs, skills, fm = data
        result: Dict[str, Any] = {}

        logger.info("[1/6] Resume analysis …")
        result["resumes"]  = self._eda_resumes(resumes, skills)

        logger.info("[2/6] Job analysis …")
        result["jobs"]     = self._eda_jobs(jobs, skills)

        logger.info("[3/6] Skills analysis …")
        result["skills"]   = self._eda_skills(skills, resumes, jobs)

        logger.info("[4/6] Feature matrix analysis …")
        result["features"] = self._eda_features(fm)

        logger.info("[5/6] Label analysis …")
        result["labels"]   = self._eda_labels(fm, resumes, jobs)

        logger.info("[6/6] Overview …")
        result["overview"] = self._eda_overview(resumes, jobs, skills, fm)

        self._save_json(result)
        self._save_markdown(result)

        logger.info("=" * 56)
        logger.info("  EDA done — charts in: %s", self.out_dir)
        logger.info("=" * 56)
        return result

    # ── data loader ───────────────────────────────────────────────────────────
    def _load(self):
        try:
            resumes = pd.read_csv(self.interim / "resumes_clean.csv")
            jobs    = pd.read_csv(self.interim / "jobs_clean.csv")
            skills  = pd.read_csv(self.interim / "skills_clean.csv")
            logger.info("  resumes=%d  jobs=%d  skills=%d", len(resumes), len(jobs), len(skills))
        except FileNotFoundError as exc:
            logger.error("Missing interim data: %s", exc)
            return None

        fm_path = self.feat_dir / "feature_matrix.csv"
        fm = pd.read_csv(fm_path) if fm_path.exists() else pd.DataFrame()
        if fm.empty:
            logger.warning("  feature_matrix.csv not found — feature/label charts skipped")
        else:
            logger.info("  feature_matrix=%d rows", len(fm))

        return resumes, jobs, skills, fm

    # ══════════════════════════════════════════════════════════════════════════
    # 1. RESUME EDA — 5 charts
    # ══════════════════════════════════════════════════════════════════════════
    def _eda_resumes(self, df: pd.DataFrame, skills: pd.DataFrame) -> dict:
        skill_list = skills["skill"].str.lower().tolist()
        df = df.copy()
        df["word_count"]  = df["resume_text"].astype(str).apply(lambda x: len(x.split()))
        df["char_len"]    = df["resume_text"].astype(str).str.len()
        df["skill_count"] = df["resume_text"].apply(
            lambda t: sum(1 for s in skill_list if s in t.lower()))

        # Chart 01 — category count (horizontal bar) ─────────────────────────
        if "category" in df.columns:
            cat = df["category"].value_counts()
            fig, ax = plt.subplots(figsize=(12, 7))
            clrs = [_PAL[i % len(_PAL)] for i in range(len(cat))]
            bars = ax.barh(cat.index[::-1], cat.values[::-1], color=clrs[::-1], height=0.72)
            for b, v in zip(bars, cat.values[::-1]):
                ax.text(b.get_width() + 0.8, b.get_y() + b.get_height() / 2,
                        str(v), va="center", fontsize=9)
            ax.set_xlabel("Number of Resumes")
            ax.set_title("01 · Resume Count per Category")
            ax.set_xlim(0, cat.max() * 1.14)
            fig.tight_layout()
            _save(fig, self.out_dir, "01_resume_category_count.png")
        else:
            logger.warning("  'category' column not found in resumes — Chart 01 skipped")

        # Chart 02 — word count + char length histograms ──────────────────────
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        for ax, col, title, c in zip(
                axes,
                ["word_count", "char_len"],
                ["Word Count per Resume", "Character Length per Resume"],
                [_PAL[0], _PAL[2]]):
            ax.hist(df[col], bins=40, color=c, edgecolor=_BG, linewidth=0.3)
            mean_v = df[col].mean()
            ax.axvline(mean_v, color=_PAL[1], lw=1.8, linestyle="--",
                       label=f"mean = {mean_v:,.0f}")
            ax.set_title(title)
            ax.set_xlabel(col.replace("_", " ").title())
            ax.legend(fontsize=9)
        fig.suptitle("02 · Resume Text Length Distribution", fontsize=13, fontweight="bold")
        fig.tight_layout()
        _save(fig, self.out_dir, "02_resume_text_length.png")

        # Chart 03 — avg skills per category ──────────────────────────────────
        if "category" in df.columns:
            sc = df.groupby("category")["skill_count"].mean().sort_values()
            fig, ax = plt.subplots(figsize=(12, 7))
            clrs = [_PAL[1] if v >= sc.median() else _PAL[8] for v in sc.values]
            bars = ax.barh(sc.index, sc.values, color=clrs, height=0.72)
            for b, v in zip(bars, sc.values):
                ax.text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2,
                        f"{v:.1f}", va="center", fontsize=9)
            ax.axvline(sc.mean(), color=_PAL[0], lw=1.5, linestyle="--",
                       label=f"mean = {sc.mean():.1f}")
            ax.set_xlabel("Avg Skill Matches per Resume")
            ax.set_title("03 · Avg Skill Count per Category  (297-skill database)")
            ax.legend()
            _save(fig, self.out_dir, "03_resume_skills_per_category.png")
        else:
            logger.warning("  'category' column not found in resumes — Chart 03 skipped")

        # Chart 04 — skill count histogram ────────────────────────────────────
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df["skill_count"], bins=30, color=_PAL[4], edgecolor=_BG, linewidth=0.3)
        mean_s = df["skill_count"].mean()
        ax.axvline(mean_s, color=_PAL[0], lw=1.8, linestyle="--",
                   label=f"mean = {mean_s:.1f}")
        ax.set_title("04 · Distribution of Skill Matches per Resume")
        ax.set_xlabel("Skills Found in Resume")
        ax.set_ylabel("Number of Resumes")
        ax.legend()
        _save(fig, self.out_dir, "04_resume_skill_count_hist.png")

        # Chart 05 — word count boxplot by category ───────────────────────────
        if "category" in df.columns:
            order = (df.groupby("category")["word_count"]
                       .median().sort_values(ascending=False).index)
            fig, ax = plt.subplots(figsize=(14, 6))
            bp = ax.boxplot(
                [df[df["category"] == c]["word_count"].values for c in order],
                labels=order, patch_artist=True,
                medianprops={"color": _PAL[0], "linewidth": 2},
                flierprops={"marker": ".", "color": _MUTED, "markersize": 3})
            for i, patch in enumerate(bp["boxes"]):
                patch.set_facecolor(_PAL[i % len(_PAL)])
                patch.set_alpha(0.7)
            ax.set_xticklabels(order, rotation=45, ha="right", fontsize=8)
            ax.set_ylabel("Word Count")
            ax.set_title("05 · Resume Word Count Boxplot by Category")
            fig.tight_layout()
            _save(fig, self.out_dir, "05_resume_wordcount_boxplot.png")
        else:
            logger.warning("  'category' column not found in resumes — Chart 05 skipped")

        return {
            "total": len(df),
            "categories": int(df["category"].nunique()) if "category" in df.columns else 0,
            "avg_word_count": round(float(df["word_count"].mean()), 1),
            "avg_char_len":   round(float(df["char_len"].mean()), 1),
            "avg_skill_count": round(float(df["skill_count"].mean()), 2),
            "resumes_with_0_skills": int((df["skill_count"] == 0).sum()),
        }

    # ══════════════════════════════════════════════════════════════════════════
    # 2. JOB EDA — 3 charts
    # ══════════════════════════════════════════════════════════════════════════
    def _eda_jobs(self, df: pd.DataFrame, skills: pd.DataFrame) -> dict:
        skill_list = skills["skill"].str.lower().tolist()
        df = df.copy()
        df["word_count"]  = df["job_text"].astype(str).apply(lambda x: len(x.split()))
        df["char_len"]    = df["job_text"].astype(str).str.len()
        df["skill_count"] = df["job_text"].apply(
            lambda t: sum(1 for s in skill_list if s in t.lower()))

        # Chart 06 — jobs per category ────────────────────────────────────────
        if "category" in df.columns:
            cat = df["category"].value_counts()
            fig, ax = plt.subplots(figsize=(12, 7))
            clrs = [_PAL[i % len(_PAL)] for i in range(len(cat))]
            bars = ax.barh(cat.index[::-1], cat.values[::-1], color=clrs[::-1], height=0.72)
            for b, v in zip(bars, cat.values[::-1]):
                ax.text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2,
                        str(v), va="center", fontsize=9)
            ax.set_xlabel("Number of Job Postings")
            ax.set_title("06 · Job Postings per Category")
            _save(fig, self.out_dir, "06_job_category_count.png")

            # Chart 07 — avg word count per job category ──────────────────────────
            wc = df.groupby("category")["word_count"].mean().sort_values()
            fig, ax = plt.subplots(figsize=(12, 7))
            clrs = [_PAL[2] if v >= wc.median() else _PAL[8] for v in wc.values]
            bars = ax.barh(wc.index, wc.values, color=clrs, height=0.72)
            for b, v in zip(bars, wc.values):
                ax.text(b.get_width() + 0.3, b.get_y() + b.get_height() / 2,
                        f"{v:.0f}", va="center", fontsize=9)
            ax.axvline(wc.mean(), color=_PAL[0], lw=1.5, linestyle="--",
                       label=f"mean = {wc.mean():.0f} words")
            ax.set_xlabel("Avg Word Count")
            ax.set_title("07 · Avg Job Description Word Count per Category")
            ax.legend()
            _save(fig, self.out_dir, "07_job_wordcount_by_category.png")

            # Chart 08 — avg skills per job category ──────────────────────────────
            sc = df.groupby("category")["skill_count"].mean().sort_values()
            fig, ax = plt.subplots(figsize=(12, 7))
            bars = ax.barh(sc.index, sc.values, color=_PAL[1], height=0.72)
            for b, v in zip(bars, sc.values):
                ax.text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2,
                        f"{v:.1f}", va="center", fontsize=9)
            ax.set_xlabel("Avg Skills per Job Description")
            ax.set_title("08 · Avg Skill Count per Job Category")
            _save(fig, self.out_dir, "08_job_skills_per_category.png")
        else:
            logger.warning("  'category' column not found in jobs — Charts 06, 07, 08 skipped")

        return {
            "total": len(df),
            "categories": int(df["category"].nunique()) if "category" in df.columns else 0,
            "avg_word_count":  round(float(df["word_count"].mean()), 1),
            "avg_skill_count": round(float(df["skill_count"].mean()), 2),
        }

    # ══════════════════════════════════════════════════════════════════════════
    # 3. SKILLS EDA — 4 charts
    # ══════════════════════════════════════════════════════════════════════════
    def _eda_skills(self, skills: pd.DataFrame,
                    resumes: pd.DataFrame, jobs: pd.DataFrame) -> dict:
        skill_list = skills["skill"].str.lower().tolist()
        all_resume  = " ".join(resumes["resume_text"].astype(str).str.lower())
        all_job     = " ".join(jobs["job_text"].astype(str).str.lower())

        res_freq = pd.Series(
            {s: all_resume.count(s) for s in skill_list}
        ).sort_values(ascending=False)
        job_freq = pd.Series(
            {s: all_job.count(s) for s in skill_list}
        ).sort_values(ascending=False)

        res_clean = res_freq[~res_freq.index.isin(_NOISE)]
        job_clean = job_freq[~job_freq.index.isin(_NOISE)]

        # Chart 09 — top 25 skills in resumes ─────────────────────────────────
        top25 = res_clean.head(25)
        fig, ax = plt.subplots(figsize=(12, 8))
        clrs = [_PAL[i % len(_PAL)] for i in range(len(top25))]
        bars = ax.barh(top25.index[::-1], top25.values[::-1],
                       color=clrs[::-1], height=0.72)
        for b, v in zip(bars, top25.values[::-1]):
            ax.text(b.get_width() + 5, b.get_y() + b.get_height() / 2,
                    f"{v:,}", va="center", fontsize=9)
        ax.set_xlabel("Frequency in Resume Corpus")
        ax.set_title("09 · Top 25 Skills — Resume Corpus")
        _save(fig, self.out_dir, "09_top25_skills_resumes.png")

        # Chart 10 — top 20 skills in jobs ────────────────────────────────────
        top20j = job_clean.head(20)
        fig, ax = plt.subplots(figsize=(12, 7))
        bars = ax.barh(top20j.index[::-1], top20j.values[::-1],
                       color=_PAL[1], height=0.72)
        for b, v in zip(bars, top20j.values[::-1]):
            ax.text(b.get_width() + 0.1, b.get_y() + b.get_height() / 2,
                    str(v), va="center", fontsize=9)
        ax.set_xlabel("Frequency in Job Descriptions")
        ax.set_title("10 · Top 20 Skills — Job Descriptions")
        _save(fig, self.out_dir, "10_top20_skills_jobs.png")

        # Chart 11 — skill domain pie ──────────────────────────────────────────
        domains = {
            "Programming":   ["python","java","javascript","typescript","kotlin","scala","ruby","swift","php","bash","r","go","rust"],
            "Web/Frameworks":["react","angular","vue","node.js","django","flask","fastapi","spring boot","express.js","next.js","laravel","rails"],
            "Databases":     ["sql","mysql","postgresql","mongodb","redis","elasticsearch","oracle","sqlite","dynamodb","snowflake","bigquery","redshift"],
            "Cloud/DevOps":  ["aws","azure","gcp","docker","kubernetes","terraform","ansible","jenkins","github actions","ci/cd","linux"],
            "Data & ML/AI":  ["machine learning","deep learning","nlp","natural language processing","tensorflow","pytorch","scikit-learn","keras","xgboost","pandas","numpy","spark","airflow","data science"],
            "Business/Fin":  ["financial analysis","financial modeling","excel","accounting","budgeting","gaap","cpa","auditing","risk management","valuation","sap"],
            "Sales/Mktg":    ["salesforce","hubspot","crm","digital marketing","seo","google ads","email marketing","content marketing","google analytics","marketo"],
            "Project Mgmt":  ["project management","agile","scrum","kanban","jira","confluence","pmp","stakeholder management","product management"],
            "Design":        ["figma","sketch","adobe photoshop","adobe illustrator","ux design","ui design","wireframing","prototyping","graphic design","after effects","premiere pro"],
            "HR/People":     ["talent acquisition","recruitment","performance management","employee relations","compensation and benefits","hris","workday","bamboohr"],
            "Soft Skills":   ["communication","leadership","teamwork","problem solving","negotiation","customer service","conflict resolution","mentoring","coaching","time management"],
            "Other Tech":    ["git","github","api integration","unit testing","test automation","quality assurance","technical writing","cybersecurity","penetration testing"],
        }
        domain_counts = {d: len([s for s in sl if s in skill_list])
                         for d, sl in domains.items()}
        fig, ax = plt.subplots(figsize=(10, 7))
        wedges, texts, autotexts = ax.pie(
            domain_counts.values(),
            labels=domain_counts.keys(),
            colors=[_PAL[i % len(_PAL)] for i in range(len(domain_counts))],
            autopct=lambda p: f"{p:.0f}%" if p > 3 else "",
            startangle=140, pctdistance=0.78)
        for t in texts: t.set_fontsize(9)
        ax.set_title("11 · Skills Database — Domain Breakdown  (297 skills)")
        _save(fig, self.out_dir, "11_skill_domain_pie.png")

        # Chart 12 — skill presence heatmap (top 15 skills × top 12 categories)
        if "category" in resumes.columns:
            top15 = res_clean.head(15).index.tolist()
            cats12 = resumes["category"].value_counts().head(12).index
            mat = []
            for cat in cats12:
                cat_text = " ".join(
                    resumes[resumes["category"] == cat]["resume_text"].astype(str).str.lower())
                mat.append([cat_text.count(s) for s in top15])
            heat = pd.DataFrame(mat, index=cats12, columns=top15)
            heat_norm = heat.div(heat.max(axis=1) + 1, axis=0)

            fig, ax = plt.subplots(figsize=(14, 7))
            sns.heatmap(heat_norm, ax=ax, cmap="YlOrRd",
                        linewidths=0.4, linecolor=_GRID, annot=False,
                        cbar_kws={"label": "Relative Skill Density"})
            ax.set_title("12 · Skill Presence Heatmap — Top 15 Skills × Resume Categories")
            ax.set_xlabel("Skill")
            ax.set_ylabel("Category")
            plt.xticks(rotation=40, ha="right", fontsize=9)
            plt.yticks(fontsize=9)
            _save(fig, self.out_dir, "12_skill_heatmap.png")
        else:
            logger.warning("  'category' column not found in resumes — Chart 12 skipped")

        return {
            "total_skills":      len(skill_list),
            "top5_in_resumes":   res_clean.head(5).index.tolist(),
            "top5_in_jobs":      job_clean.head(5).index.tolist(),
        }

    # ══════════════════════════════════════════════════════════════════════════
    # 4. FEATURE MATRIX EDA — 4 charts
    # ══════════════════════════════════════════════════════════════════════════
    def _eda_features(self, fm: pd.DataFrame) -> dict:
        if fm.empty:
            return {}

        num_cols = [c for c in [
            "tfidf_similarity","embedding_similarity","skill_match_ratio",
            "skill_overlap_count","keyword_overlap","resume_word_count",
            "job_word_count","readability_score","skill_density",
            "resume_quality_score"] if c in fm.columns]

        # Chart 13 — grid of feature histograms ───────────────────────────────
        ncols = 3
        nrows = -(-len(num_cols) // ncols)
        fig, axes = plt.subplots(nrows, ncols, figsize=(14, nrows * 3.2))
        axes = axes.flatten()
        for i, col in enumerate(num_cols):
            ax = axes[i]
            ax.hist(fm[col].dropna(), bins=40,
                    color=_PAL[i % len(_PAL)], edgecolor=_BG, linewidth=0.3)
            mean_v = fm[col].mean()
            ax.axvline(mean_v, color=_PAL[0], lw=1.4, linestyle="--",
                       label=f"μ={mean_v:.3f}")
            ax.set_title(col, fontsize=9)
            ax.tick_params(labelsize=7)
            ax.legend(fontsize=7)
        for j in range(len(num_cols), len(axes)):
            axes[j].set_visible(False)
        fig.suptitle("13 · Feature Value Distributions", fontsize=13,
                     fontweight="bold", y=1.01)
        fig.tight_layout()
        _save(fig, self.out_dir, "13_feature_distributions.png")

        # Chart 14 — correlation heatmap ──────────────────────────────────────
        corr = fm[num_cols].corr()
        fig, ax = plt.subplots(figsize=(11, 9))
        sns.heatmap(corr, ax=ax,
                    mask=np.triu(np.ones_like(corr, dtype=bool)),
                    cmap="coolwarm", center=0, vmin=-1, vmax=1,
                    annot=True, fmt=".2f", annot_kws={"size": 8},
                    linewidths=0.5, linecolor=_GRID)
        ax.set_title("14 · Feature Correlation Matrix")
        plt.xticks(rotation=40, ha="right", fontsize=9)
        plt.yticks(fontsize=9)
        _save(fig, self.out_dir, "14_feature_correlation.png")

        # Chart 15 — boxplots (outlier detection) ─────────────────────────────
        fig, axes = plt.subplots(2, 5, figsize=(16, 6))
        axes = axes.flatten()
        for i, col in enumerate(num_cols[:10]):
            ax = axes[i]
            ax.boxplot(fm[col].dropna(), patch_artist=True,
                       boxprops={"facecolor": _PAL[i % len(_PAL)], "alpha": 0.7},
                       medianprops={"color": _INK, "linewidth": 2},
                       whiskerprops={"color": _MUTED},
                       capprops={"color": _MUTED},
                       flierprops={"marker": ".", "color": _MUTED, "markersize": 3})
            ax.set_title(col, fontsize=8)
            ax.tick_params(labelsize=7)
        fig.suptitle("15 · Feature Boxplots — Outlier Detection",
                     fontsize=13, fontweight="bold")
        fig.tight_layout()
        _save(fig, self.out_dir, "15_feature_boxplots.png")

        # Chart 16 — pairplot coloured by label (sampled 2 k rows) ────────────
        key = [c for c in ["tfidf_similarity","embedding_similarity",
                            "keyword_overlap","skill_match_ratio"] if c in fm.columns]
        if "label" in fm.columns and len(key) >= 3:
            sample = (fm[key + ["label"]].dropna()
                        .sample(min(2000, len(fm)), random_state=42))
            sample["label"] = sample["label"].astype(str)
            pair = sns.pairplot(sample, hue="label",
                                palette={"0": _PAL[8], "1": _PAL[0]},
                                plot_kws={"alpha": 0.3, "s": 10},
                                diag_kws={"linewidth": 1.2})
            pair.figure.suptitle("16 · Pairplot — Key Features by Label",
                                 y=1.02, fontsize=12, fontweight="bold")
            pair.figure.set_facecolor(_BG)
            _save(pair.figure, self.out_dir, "16_feature_pairplot.png")

        return fm[num_cols].describe().round(4).to_dict()

    # ══════════════════════════════════════════════════════════════════════════
    # 5. LABEL ANALYSIS — 3 charts
    # ══════════════════════════════════════════════════════════════════════════
    def _eda_labels(self, fm: pd.DataFrame,
                    resumes: pd.DataFrame, jobs: pd.DataFrame) -> dict:
        if fm.empty or "label" not in fm.columns:
            return {}

        pos   = int((fm["label"] == 1).sum())
        neg   = int((fm["label"] == 0).sum())
        total = len(fm)

        # Chart 17 — current label pie + bar ──────────────────────────────────
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
        ax1.pie([neg, pos],
                labels=[f"No Match (0)\n{neg:,}", f"Match (1)\n{pos:,}"],
                colors=[_PAL[8], _PAL[0]],
                autopct="%1.1f%%", startangle=90,
                wedgeprops={"edgecolor": _BG, "linewidth": 2})
        ax1.set_title("Label Split")

        ax2.bar(["No Match (0)", "Match (1)"], [neg, pos],
                color=[_PAL[8], _PAL[0]], width=0.5, edgecolor=_BG)
        ax2.set_ylabel("Count")
        ax2.set_title("Label Counts")
        for i, v in enumerate([neg, pos]):
            ax2.text(i, v + total * 0.005, f"{v:,}", ha="center", fontsize=11)
        fig.suptitle("17 · Training Label Distribution  (current feature_matrix)",
                     fontsize=12, fontweight="bold")
        _save(fig, self.out_dir, "17_label_distribution.png")

        # Chart 18 — feature distributions coloured by label ──────────────────
        feat_cols = [c for c in ["embedding_similarity","tfidf_similarity",
                                 "keyword_overlap","skill_match_ratio"]
                     if c in fm.columns]
        if feat_cols:
            fig, axes = plt.subplots(1, len(feat_cols), figsize=(14, 4))
            if len(feat_cols) == 1:
                axes = [axes]
            for ax, col in zip(axes, feat_cols):
                for lbl, color, name in [(0, _PAL[8], "No Match"),
                                          (1, _PAL[0], "Match")]:
                    ax.hist(fm[fm["label"] == lbl][col].dropna(),
                            bins=35, alpha=0.65, color=color,
                            edgecolor=_BG, linewidth=0.3,
                            label=name, density=True)
                ax.set_title(col, fontsize=10)
                ax.legend(fontsize=8)
            fig.suptitle("18 · Feature Distributions — Match vs No Match",
                         fontsize=12, fontweight="bold")
            fig.tight_layout()
            _save(fig, self.out_dir, "18_features_by_label.png")

        # Chart 19 — expected positive labels per category (new dataset) ──────
        if "category" in jobs.columns:
            cat_pos = {
                cat: int((resumes["category"] == cat).sum() *
                         (jobs["category"] == cat).sum())
                for cat in resumes["category"].unique()
            }
            cat_s = pd.Series(cat_pos).sort_values()
            fig, ax = plt.subplots(figsize=(12, 7))
            clrs = [_PAL[0] if v > 0 else _PAL[8] for v in cat_s.values]
            bars = ax.barh(cat_s.index, cat_s.values, color=clrs, height=0.72)
            for b, v in zip(bars, cat_s.values):
                ax.text(b.get_width() + 2, b.get_y() + b.get_height() / 2,
                        f"{v:,}", va="center", fontsize=9)
            ax.set_xlabel("Positive Pairs  (resume × matching jobs)")
            ax.set_title("19 · Expected Positive Labels per Category\n"
                         "(after re-running feature engineering with new data)")
            red_p  = mpatches.Patch(color=_PAL[0], label="Has job descriptions")
            grey_p = mpatches.Patch(color=_PAL[8], label="No job descriptions")
            ax.legend(handles=[red_p, grey_p])
            _save(fig, self.out_dir, "19_expected_labels_by_category.png")

            exp_pos = sum(cat_pos.values())
            exp_neg = len(resumes) * len(jobs) - exp_pos
        else:
            exp_pos, exp_neg = 0, 0

        return {
            "current_positive":       pos,
            "current_negative":       neg,
            "current_positive_pct":   round(pos / total * 100, 2),
            "expected_positive_new":  exp_pos,
            "expected_negative_new":  exp_neg,
        }

    # ══════════════════════════════════════════════════════════════════════════
    # 6. OVERVIEW — 2 charts
    # ══════════════════════════════════════════════════════════════════════════
    def _eda_overview(self, resumes, jobs, skills, fm) -> dict:
        # Chart 20 — dataset sizes bar ─────────────────────────────────────────
        sizes = {
            "Resumes":    len(resumes),
            "Jobs":       len(jobs),
            "Skills":     len(skills),
            "Feat Pairs\n(÷1000)": len(fm) // 1000 if not fm.empty else 0,
        }
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(list(sizes.keys()), list(sizes.values()),
                      color=_PAL[:4], width=0.5, edgecolor=_BG)
        for b, v in zip(bars, sizes.values()):
            ax.text(b.get_x() + b.get_width() / 2,
                    b.get_height() + max(sizes.values()) * 0.01,
                    f"{v:,}", ha="center", fontsize=11, fontweight="bold")
        ax.set_ylabel("Count")
        ax.set_title("20 · Dataset Sizes — Current State")
        _save(fig, self.out_dir, "20_dataset_overview.png")

        # Chart 21 — resume vs job coverage per category (grouped bar) ────────
        res_cats = set(resumes["category"].unique()) if "category" in resumes.columns else set()
        job_cats = (set(jobs["category"].unique())
                    if "category" in jobs.columns else set())
        all_cats = sorted(res_cats | job_cats)

        if all_cats:
            r_counts = [resumes[resumes["category"] == c].shape[0] if "category" in resumes.columns else 0 for c in all_cats]
            j_counts = [len(jobs[jobs["category"] == c])
                        if "category" in jobs.columns else 0
                        for c in all_cats]

            x = np.arange(len(all_cats))
            w = 0.38
            fig, ax = plt.subplots(figsize=(15, 6))
            ax.bar(x - w / 2, r_counts, w, label="Resumes", color=_PAL[0], alpha=0.85)
            ax.bar(x + w / 2, j_counts, w, label="Jobs",    color=_PAL[1], alpha=0.85)
            ax.set_xticks(x)
            ax.set_xticklabels(all_cats, rotation=45, ha="right", fontsize=8)
            ax.set_ylabel("Count")
            ax.set_title("21 · Resume vs Job Coverage by Category")
            ax.legend()
            fig.tight_layout()
            _save(fig, self.out_dir, "21_resume_vs_job_coverage.png")
        else:
            logger.warning("  No categories found in resumes or jobs — Chart 21 skipped")

        return {
            "resume_categories":         len(res_cats),
            "job_categories":            len(job_cats),
            "categories_with_both":      len(res_cats & job_cats),
            "categories_missing_jobs":   sorted(res_cats - job_cats),
        }

    # ── persist outputs ───────────────────────────────────────────────────────
    def _save_json(self, summary: dict) -> None:
        path = self.out_dir / "eda_summary.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info("  JSON  → %s", path.name)

    def _save_markdown(self, summary: dict) -> None:
        r = summary.get("resumes", {})
        j = summary.get("jobs", {})
        s = summary.get("skills", {})
        lbl = summary.get("labels", {})
        ov  = summary.get("overview", {})

        lines = [
            "# EDA Report — Bug Busters\n",
            f"Datasets: **{r.get('total','?')} resumes** · "
            f"**{j.get('total','?')} jobs** · "
            f"**{s.get('total_skills','?')} skills**\n",
            "---\n",
            "## Resumes",
            f"- Categories: {r.get('categories','?')}",
            f"- Avg word count: {r.get('avg_word_count','?')}",
            f"- Avg skills matched: **{r.get('avg_skill_count','?')}**",
            f"- Resumes with 0 skills: {r.get('resumes_with_0_skills','?')}\n",
            "## Jobs",
            f"- Categories covered: {j.get('categories','?')}",
            f"- Avg word count: {j.get('avg_word_count','?')}",
            f"- Avg skills per job: {j.get('avg_skill_count','?')}\n",
            "## Skills",
            f"- Total: **{s.get('total_skills','?')}**",
            f"- Top 5 in resumes: {s.get('top5_in_resumes',[])}",
            f"- Top 5 in jobs: {s.get('top5_in_jobs',[])}\n",
            "## Labels",
            f"- Current positive: {lbl.get('current_positive','?')} "
            f"({lbl.get('current_positive_pct','?')}%)",
            f"- Expected positive after re-run: **{lbl.get('expected_positive_new','?')}** (~4.2%)\n",
            "## Category Coverage",
            f"- Categories with both resumes & jobs: "
            f"**{ov.get('categories_with_both','?')}**",
            f"- Missing jobs: {ov.get('categories_missing_jobs',[])}\n",
            "## Charts  (outputs/reports/eda/)",
            "| # | File | What it shows |",
            "|---|------|---------------|",
            "| 01 | 01_resume_category_count.png      | Resume count per category |",
            "| 02 | 02_resume_text_length.png         | Word & char length histograms |",
            "| 03 | 03_resume_skills_per_category.png | Avg skill matches per category |",
            "| 04 | 04_resume_skill_count_hist.png    | Skill count histogram |",
            "| 05 | 05_resume_wordcount_boxplot.png   | Word count boxplot by category |",
            "| 06 | 06_job_category_count.png         | Job postings per category |",
            "| 07 | 07_job_wordcount_by_category.png  | Avg job description word count |",
            "| 08 | 08_job_skills_per_category.png    | Avg skills per job category |",
            "| 09 | 09_top25_skills_resumes.png       | Top 25 skills in resume corpus |",
            "| 10 | 10_top20_skills_jobs.png          | Top 20 skills in job descriptions |",
            "| 11 | 11_skill_domain_pie.png           | Skill domain breakdown (pie) |",
            "| 12 | 12_skill_heatmap.png              | Skill presence heatmap |",
            "| 13 | 13_feature_distributions.png     | All 10 feature histograms |",
            "| 14 | 14_feature_correlation.png       | Feature correlation heatmap |",
            "| 15 | 15_feature_boxplots.png           | Feature boxplots (outliers) |",
            "| 16 | 16_feature_pairplot.png           | Pairplot coloured by label |",
            "| 17 | 17_label_distribution.png         | Label pie + bar chart |",
            "| 18 | 18_features_by_label.png          | Feature distributions by label |",
            "| 19 | 19_expected_labels_by_category.png| Expected positive labels (new) |",
            "| 20 | 20_dataset_overview.png           | Dataset sizes summary |",
            "| 21 | 21_resume_vs_job_coverage.png     | Resume vs job category coverage |",
        ]
        path = self.out_dir / "EDA_REPORT.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        # also keep legacy summary
        (self.root / "outputs" / "reports" / "EDA_PROJECT_SUMMARY.md").write_text(
            "\n".join(lines), encoding="utf-8")
        logger.info("  MD   → %s", path.name)


# ── standalone ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s  %(levelname)s  %(message)s")
    EDAEngine().run_full_eda()
