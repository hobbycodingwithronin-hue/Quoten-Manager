from __future__ import annotations

import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_CEILING, getcontext
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QComboBox,
    QGroupBox, QFrame, QAbstractItemView, QSplitter, QScrollArea
)

getcontext().prec = 28
D = Decimal
APP_TITLE = "Betting Analyzer Pro"


def dec(value, field="Wert"):
    try:
        result = D(str(value).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field}: Bitte eine gültige Zahl eingeben.")
    if not result.is_finite():
        raise ValueError(f"{field}: Bitte eine endliche Zahl eingeben.")
    return result


def money(value, currency="€"):
    rounded = value.quantize(D("0.01"))
    s = f"{rounded:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} {currency}"


def odds_text(value, places=4):
    q = D(1).scaleb(-places)
    return str(value.quantize(q, rounding=ROUND_CEILING))


def make_label(text, style=""):
    label = QLabel(text)
    if style:
        label.setStyleSheet(style)
    return label


class StatCard(QFrame):
    def __init__(self, caption, value="—", accent="#38D9A9"):
        super().__init__()
        self.setObjectName("statCard")
        self.setMinimumHeight(82)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        self.caption = QLabel(caption.upper())
        self.caption.setObjectName("statCaption")

        self.value = QLabel(value)
        self.value.setObjectName("statValue")
        self.value.setStyleSheet(f"color: {accent};")

        layout.addWidget(self.caption)
        layout.addWidget(self.value)

    def set_value(self, value, color=None):
        self.value.setText(value)
        if color:
            self.value.setStyleSheet(f"color: {color};")


class BettingAnalyzer(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_TITLE)
        self.resize(1250, 850)
        self.setMinimumSize(1050, 700)

        self.currency = "€"
        self.starting_capital = D("1000")
        self.current_capital = D("1000")
        self.bet_history = []
        self.combo_rows = []

        self._build_ui()
        self._apply_theme()
        self.refresh_capital()

    # -------------------------------------------------
    # UI HILFSFUNKTIONEN
    # -------------------------------------------------

    def input_box(self, placeholder="", value=""):
        w = QLineEdit(str(value))
        w.setPlaceholderText(placeholder)
        w.setClearButtonEnabled(True)
        return w

    def section_title(self, title, subtitle=""):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 8)

        t = QLabel(title)
        t.setObjectName("sectionTitle")
        layout.addWidget(t)

        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("muted")
            s.setWordWrap(True)
            layout.addWidget(s)

        return w

    def make_table(self, headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setMinimumHeight(220)
        return table

    def table_item(self, text, align=Qt.AlignCenter):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        return item

    def show_error(self, message):
        QMessageBox.warning(self, "Eingabe prüfen", message)

    # -------------------------------------------------
    # HAUPTFENSTER
    # -------------------------------------------------

    def _build_ui(self):
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(22, 18, 22, 18)
        outer.setSpacing(14)

        header = QHBoxLayout()
        brand = QVBoxLayout()

        title = QLabel("BETTING ANALYZER PRO")
        title.setObjectName("appTitle")

        subtitle = QLabel(
            "Quotenanalyse  •  Absicherung  •  Kapitalübersicht"
        )
        subtitle.setObjectName("muted")

        brand.addWidget(title)
        brand.addWidget(subtitle)
        header.addLayout(brand)
        header.addStretch()

        self.currency_box = QComboBox()
        self.currency_box.addItems(["€", "USDT", "$", "£"])
        self.currency_box.currentTextChanged.connect(
            self.change_currency
        )

        header.addWidget(make_label("Währung"))
        header.addWidget(self.currency_box)
        outer.addLayout(header)

        cards = QHBoxLayout()

        self.capital_card = StatCard(
            "Aktuelles Kapital", "1.000,00 €"
        )
        self.profit_card = StatCard(
            "Bilanz seit Start", "0,00 €"
        )
        self.count_card = StatCard(
            "Erfasste Wetten", "0", "#75A7FF"
        )

        cards.addWidget(self.capital_card)
        cards.addWidget(self.profit_card)
        cards.addWidget(self.count_card)
        outer.addLayout(cards)

        self.tabs = QTabWidget()

        self.tabs.addTab(
            self.build_hedge_tab(),
            "⚖  Absicherungsrechner"
        )
        self.tabs.addTab(
            self.build_target_combo_tab(),
            "⌁  Kombi-Zielquote"
        )
        self.tabs.addTab(
            self.build_combo_tab(),
            "▦  Kombi-Analysator"
        )
        self.tabs.addTab(
            self.build_capital_tab(),
            "◈  Kapitalmanager"
        )

        outer.addWidget(self.tabs, 1)

        footer = QHBoxLayout()
        footer.addWidget(
            make_label(
                "Lokale Datenverwaltung · JSON",
                "color:#8292A8;"
            )
        )
        footer.addStretch()

        save_btn = QPushButton("Speichern")
        load_btn = QPushButton("Laden")
        reset_btn = QPushButton("Zurücksetzen")

        save_btn.clicked.connect(self.save_json)
        load_btn.clicked.connect(self.load_json)
        reset_btn.clicked.connect(self.reset_data)

        footer.addWidget(save_btn)
        footer.addWidget(load_btn)
        footer.addWidget(reset_btn)

        outer.addLayout(footer)
        self.setCentralWidget(root)

    # -------------------------------------------------
    # ABSICHERUNGSRECHNER
    # -------------------------------------------------

    def build_hedge_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(
            self.section_title(
                "Absicherungsrechner",
                "Automatische Gewinnverteilung für alle abgedeckten Ausgänge."
            )
        )

        splitter = QSplitter(Qt.Horizontal)

        left = QWidget()
        left_l = QVBoxLayout(left)

        group2 = QGroupBox("2-Wege-Wette")
        f2 = QFormLayout(group2)

        self.two_stake = self.input_box("z. B. 10,00")
        self.two_odds = self.input_box("z. B. 1,57")

        self.two_currency_note = make_label(
            "Einsatz und Zielgewinn in der gewählten Währung",
            "color:#8292A8;"
        )

        f2.addRow("Ersteinsatz", self.two_stake)
        f2.addRow("Quote Ausgang 1", self.two_odds)
        f2.addRow(self.two_currency_note)

        calc2 = QPushButton("2-Wege berechnen")
        calc2.clicked.connect(self.calculate_two_way)
        f2.addRow(calc2)

        left_l.addWidget(group2)

        group3 = QGroupBox("3-Wege-Wette (Dutching)")
        f3 = QFormLayout(group3)

        self.three_total = self.input_box("z. B. 10,00")
        self.three_o1 = self.input_box("z. B. 2,10")
        self.three_o2 = self.input_box("z. B. 3,20")

        f3.addRow("Gesamteinsatz", self.three_total)
        f3.addRow("Quote Ausgang 1", self.three_o1)
        f3.addRow("Quote Ausgang 2", self.three_o2)

        calc3 = QPushButton("3-Wege berechnen")
        calc3.clicked.connect(self.calculate_three_way)
        f3.addRow(calc3)

        left_l.addWidget(group3)
        left_l.addStretch()

        right = QWidget()
        right_l = QVBoxLayout(right)

        self.hedge_result = QLabel(
            "Gib deine Werte ein und starte die Berechnung."
        )
        self.hedge_result.setObjectName("resultPanel")
        self.hedge_result.setWordWrap(True)

        right_l.addWidget(self.hedge_result)

        self.hedge_table = self.make_table([
            "Ziel-Reingewinn",
            "Einsatz Absicherung",
            "Benötigte Gegenquote",
            "Status"
        ])

        right_l.addWidget(self.hedge_table, 1)

        note = QLabel(
            "Hinweis: Die 2-Wege-Tabelle berechnet den passenden "
            "Gegenwetteinsatz und die Gegenquote. Die 3-Wege-Rechnung "
            "verteilt den Gesamteinsatz proportional zu den Kehrwerten "
            "der Quoten."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)

        right_l.addWidget(note)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([390, 760])

        layout.addWidget(splitter, 1)
        return page

    def build_target_combo_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(
            self.section_title(
                "Kombinationsquoten-Rechner",
                "Berechnet die Mindestquote je Auswahl, damit "
                "das Produkt mindestens deine Ziel-Gesamtquote erreicht."
            )
        )

        group = QGroupBox("Zielvorgabe")
        form = QFormLayout(group)

        self.target_stake = self.input_box("z. B. 10,00")
        self.target_odds = self.input_box("z. B. 1,40")

        self.target_currency = make_label(
            "Die Zielquote bezieht sich auf die Gesamtquote, "
            "nicht auf den Gewinn."
        )
        self.target_currency.setObjectName("muted")

        form.addRow("Einsatz", self.target_stake)
        form.addRow("Gewünschte Gesamtquote", self.target_odds)
        form.addRow(self.target_currency)

        btn = QPushButton("Mindestquoten berechnen")
        btn.clicked.connect(self.calculate_target_combo)
        form.addRow(btn)

        layout.addWidget(group)

        self.target_table = self.make_table([
            "Kombi",
            "Mindestquote je Auswahl",
            "Produkt (ungekürzt)",
            "Auszahlung",
            "Reingewinn"
        ])

        layout.addWidget(self.target_table, 1)

        self.target_note = QLabel("Noch keine Berechnung.")
        self.target_note.setObjectName("muted")
        layout.addWidget(self.target_note)

        return page

    # -------------------------------------------------
    # KOMBI-ANALYSATOR
    # -------------------------------------------------

    def build_combo_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(
            self.section_title(
                "Kombi-Analysator",
                "Beliebig viele Einzelquoten eingeben. "
                "Leere Felder werden ignoriert. Jede Quote kann "
                "einzeln entfernt werden."
            )
        )

        top = QHBoxLayout()

        top.addWidget(make_label("Einsatz"))

        self.combo_stake = self.input_box("z. B. 10,00")
        self.combo_stake.setMaximumWidth(160)

        top.addWidget(self.combo_stake)
        top.addWidget(make_label("Währung: aktuelle Auswahl"))
        top.addStretch()

        add_btn = QPushButton("+ Quote hinzufügen")

        # WICHTIG: clicked sendet einen Boolean-Wert.
        # Dieser wird hier bewusst nicht an add_combo_row übergeben.
        add_btn.clicked.connect(
            lambda checked=False: self.add_combo_row()
        )

        top.addWidget(add_btn)
        layout.addLayout(top)

        self.combo_container = QWidget()
        self.combo_layout = QVBoxLayout(self.combo_container)
        self.combo_layout.setContentsMargins(0, 0, 0, 0)
        self.combo_layout.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.combo_container)
        scroll.setMinimumHeight(220)

        layout.addWidget(scroll, 1)

        actions = QHBoxLayout()

        calc = QPushButton("Gesamtkombi berechnen")
        calc.clicked.connect(self.calculate_combo)

        clear = QPushButton("Alle Quoten löschen")
        clear.clicked.connect(self.clear_combo_rows)

        actions.addWidget(calc)
        actions.addWidget(clear)
        actions.addStretch()

        layout.addLayout(actions)

        self.combo_total_card = StatCard("Gesamtquote", "—")
        self.combo_return_card = StatCard("Gesamtauszahlung", "—")
        self.combo_profit_card = StatCard("Reingewinn", "—")

        stats = QHBoxLayout()
        stats.addWidget(self.combo_total_card)
        stats.addWidget(self.combo_return_card)
        stats.addWidget(self.combo_profit_card)

        layout.addLayout(stats)

        self.add_combo_row()
        self.add_combo_row()

        return page

        # -------------------------------------------------
    # KAPITALMANAGER
    # -------------------------------------------------

    def build_capital_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(
            self.section_title(
                "Kapitalmanager",
                "Erfasse abgeschlossene Wetten mit ihrem Nettoergebnis. "
                "Jede erfasste Wette zählt als ein Eintrag."
            )
        )

        form_group = QGroupBox("Kapital und Ergebnis erfassen")
        form = QFormLayout(form_group)

        self.start_capital_input = self.input_box(
            "z. B. 1000,00", "1000"
        )
        self.bet_result_input = self.input_box(
            "z. B. 5,70 oder -10,00"
        )
        self.bet_description_input = self.input_box(
            "z. B. Team A – Team B"
        )

        form.addRow("Startkapital", self.start_capital_input)
        form.addRow(
            "Nettoergebnis dieser Wette",
            self.bet_result_input
        )
        form.addRow(
            "Beschreibung (optional)",
            self.bet_description_input
        )

        actions = QHBoxLayout()

        add = QPushButton("Wette verbuchen")
        add.clicked.connect(self.add_bet_result)

        update_start = QPushButton(
            "Startkapital übernehmen"
        )
        update_start.clicked.connect(
            self.update_start_capital
        )

        actions.addWidget(add)
        actions.addWidget(update_start)

        form.addRow(actions)
        layout.addWidget(form_group)

        self.capital_table = self.make_table([
            "Datum / Uhrzeit",
            "Beschreibung",
            "Nettoergebnis",
            "Kapital danach",
            ""
        ])

        self.capital_table.setMinimumHeight(260)
        layout.addWidget(self.capital_table, 1)

        self.capital_summary = QLabel("")
        self.capital_summary.setObjectName("muted")
        layout.addWidget(self.capital_summary)

        return page

    # -------------------------------------------------
    # DESIGN / DARK THEME
    # -------------------------------------------------

    def _apply_theme(self):
        self.setStyleSheet("""
            QWidget {
                background: #101722;
                color: #E8EEF7;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }

            QMainWindow {
                background: #101722;
            }

            QLabel#appTitle {
                font-size: 22pt;
                font-weight: 800;
                letter-spacing: 1px;
                color: #F5F8FC;
            }

            QLabel#sectionTitle {
                font-size: 17pt;
                font-weight: 700;
                color: #F5F8FC;
            }

            QLabel#muted {
                color: #91A1B5;
            }

            QTabWidget::pane {
                border: 1px solid #29384A;
                border-radius: 10px;
                top: -1px;
            }

            QTabBar::tab {
                background: #182332;
                color: #AAB8C9;
                padding: 12px 18px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }

            QTabBar::tab:selected {
                background: #233448;
                color: #38D9A9;
                font-weight: 700;
            }

            QGroupBox {
                border: 1px solid #2B3B4E;
                border-radius: 10px;
                margin-top: 12px;
                padding: 14px;
                font-weight: 700;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #38D9A9;
            }

            QLineEdit, QComboBox {
                background: #182332;
                border: 1px solid #34475D;
                border-radius: 7px;
                padding: 9px;
                color: #F2F6FA;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #38D9A9;
            }

            QPushButton {
                background: #233448;
                border: 1px solid #3B526B;
                border-radius: 7px;
                padding: 9px 14px;
                color: #F2F6FA;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #2D455E;
                border-color: #38D9A9;
            }

            QPushButton:pressed {
                background: #1B2A39;
            }

            QTableWidget {
                background: #15202D;
                alternate-background-color: #192737;
                border: 1px solid #2B3B4E;
                border-radius: 8px;
                gridline-color: #2B3B4E;
            }

            QHeaderView::section {
                background: #233448;
                color: #DCE6F2;
                border: none;
                padding: 9px;
                font-weight: 700;
            }

            QTableWidget::item {
                padding: 7px;
            }

            QScrollArea {
                border: none;
            }

            QFrame#statCard {
                background: #1A2837;
                border: 1px solid #2C4054;
                border-radius: 10px;
            }

            QLabel#statCaption {
                color: #91A1B5;
                font-size: 8pt;
                font-weight: 700;
            }

            QLabel#statValue {
                color: #38D9A9;
                font-size: 18pt;
                font-weight: 800;
            }

            QLabel#resultPanel {
                background: #1A2837;
                border: 1px solid #2C4054;
                border-radius: 10px;
                padding: 16px;
                color: #EAF2FA;
            }

            QComboBox QAbstractItemView {
                background: #182332;
                selection-background-color: #2D455E;
            }
        """)

    # -------------------------------------------------
    # 2-WEGE-ABSICHERUNG
    # -------------------------------------------------

    def calculate_two_way(self):
        try:
            stake = dec(
                self.two_stake.text(),
                "Ersteinsatz"
            )
            odds = dec(
                self.two_odds.text(),
                "Quote"
            )

            if stake <= 0 or odds <= 1:
                raise ValueError(
                    "Der Einsatz muss größer 0 und "
                    "die Quote größer 1 sein."
                )

            first_profit = stake * (odds - 1)

            targets = [
                D("0"),
                D("1"),
                D("2.5"),
                D("5"),
                D("10")
            ]

            self.hedge_table.setRowCount(0)

            for target in targets:
                hedge_stake = first_profit - target

                row = self.hedge_table.rowCount()
                self.hedge_table.insertRow(row)

                if hedge_stake <= 0:
                    values = [
                        money(target, self.currency),
                        "—",
                        "Nicht möglich",
                        "Ziel zu hoch"
                    ]
                else:
                    required_odds = (
                        D(1) + (stake + target) / hedge_stake
                    )

                    values = [
                        money(target, self.currency),
                        money(hedge_stake, self.currency),
                        odds_text(required_odds),
                        "Machbar"
                    ]

                for col, value in enumerate(values):
                    self.hedge_table.setItem(
                        row,
                        col,
                        self.table_item(value)
                    )

            self.hedge_result.setText(
                f"Erste Wette: {money(stake, self.currency)} "
                f"auf Quote {odds_text(odds, 2)}\n"
                f"Gewinn bei Ausgang 1 ohne Absicherung: "
                f"{money(first_profit, self.currency)}\n\n"
                "Die Tabelle zeigt für jeden Zielgewinn den "
                "passenden Gegenwetteinsatz und die notwendige "
                "Gegenquote, bei der beide Ausgänge denselben "
                "Nettogewinn liefern."
            )

        except ValueError as e:
            self.show_error(str(e))

    # -------------------------------------------------
    # 3-WEGE-ABSICHERUNG
    # -------------------------------------------------

    def calculate_three_way(self):
        try:
            total = dec(
                self.three_total.text(),
                "Gesamteinsatz"
            )
            o1 = dec(
                self.three_o1.text(),
                "Quote Ausgang 1"
            )
            o2 = dec(
                self.three_o2.text(),
                "Quote Ausgang 2"
            )

            if total <= 0 or o1 <= 1 or o2 <= 1:
                raise ValueError(
                    "Der Gesamteinsatz muss größer 0 und "
                    "beide Quoten müssen größer 1 sein."
                )

            targets = [
                D("0"),
                D("1"),
                D("2.5"),
                D("5"),
                D("10")
            ]

            self.hedge_table.setRowCount(0)

            reciprocal_sum = (
                D(1) / o1 + D(1) / o2
            )

            for target in targets:

                required_sum = (
                    D(1) / (D(1) + target / total)
                )

                remaining = required_sum - reciprocal_sum

                row = self.hedge_table.rowCount()
                self.hedge_table.insertRow(row)

                if remaining <= 0:
                    values = [
                        money(target, self.currency),
                        "—",
                        "Nicht möglich",
                        "Ziel/Quoten ungeeignet"
                    ]

                else:
                    o3 = D(1) / remaining

                    inv_sum = (
                        reciprocal_sum + D(1) / o3
                    )

                    stake3 = (
                        total * (D(1) / o3) / inv_sum
                    )

                    values = [
                        money(target, self.currency),
                        f"{money(stake3, self.currency)} (Ausgang 3)",
                        odds_text(o3),
                        "Machbar"
                    ]

                for col, value in enumerate(values):
                    self.hedge_table.setItem(
                        row,
                        col,
                        self.table_item(value)
                    )

            self.hedge_result.setText(
                f"3-Wege-Dutching · Gesamteinsatz "
                f"{money(total, self.currency)}\n"
                f"Quote 1: {odds_text(o1, 2)} · "
                f"Quote 2: {odds_text(o2, 2)}\n\n"
                "Die dritte Quote wird so bestimmt, dass der "
                "Gesamteinsatz proportional auf alle drei "
                "Ausgänge verteilt werden kann und der gewünschte "
                "gleiche Nettogewinn entsteht. Die Einsatzspalte "
                "zeigt den Anteil für Ausgang 3."
            )

        except ValueError as e:
            self.show_error(str(e))

    # -------------------------------------------------
    # KOMBINATIONSQUOTEN-RECHNER
    # -------------------------------------------------

    def calculate_target_combo(self):
        try:
            stake = dec(
                self.target_stake.text(),
                "Einsatz"
            )
            target = dec(
                self.target_odds.text(),
                "Ziel-Gesamtquote"
            )

            if stake <= 0 or target <= 1:
                raise ValueError(
                    "Der Einsatz muss größer 0 und "
                    "die Ziel-Gesamtquote größer 1 sein."
                )

            self.target_table.setRowCount(0)

            for n in range(2, 6):

                raw = target ** (D(1) / D(n))
                step = D("0.0001")

                per_leg = (
                    (raw / step).to_integral_value(
                        rounding=ROUND_CEILING
                    ) * step
                )

                product = per_leg ** n

                while product < target:
                    per_leg += step
                    product = per_leg ** n

                payout = stake * product
                profit = payout - stake

                row = self.target_table.rowCount()
                self.target_table.insertRow(row)

                vals = [
                    f"{n}-er-Kombi",
                    odds_text(per_leg, 4),
                    odds_text(product, 6),
                    money(payout, self.currency),
                    money(profit, self.currency)
                ]

                for col, value in enumerate(vals):
                    self.target_table.setItem(
                        row,
                        col,
                        self.table_item(value)
                    )

            self.target_note.setText(
                f"Ziel-Gesamtquote: {odds_text(target, 4)}. "
                "Die angezeigte Einzelquote wird aufgerundet, "
                "damit das Produkt der angezeigten Quoten die "
                "Zielquote garantiert erreicht oder übertrifft."
            )

        except (ValueError, InvalidOperation) as e:
            self.show_error(str(e))

        # -------------------------------------------------
    # KOMBI-ANALYSATOR
    # -------------------------------------------------

    def add_combo_row(self, value=""):
        # Beliebig viele Quoten hinzufügen.
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        number = QLabel(
            f"Quote {len(self.combo_rows) + 1}"
        )
        number.setMinimumWidth(75)

        edit = self.input_box(
            "Quote eingeben, z. B. 1,45",
            value
        )

        remove = QPushButton("Entfernen")
        remove.setMaximumWidth(110)

        remove.clicked.connect(
            lambda checked=False: self.remove_combo_row(
                row, edit
            )
        )

        row_layout.addWidget(number)
        row_layout.addWidget(edit, 1)
        row_layout.addWidget(remove)

        self.combo_layout.addWidget(row)
        self.combo_rows.append(edit)

    def remove_combo_row(self, row_widget, edit):
        if edit in self.combo_rows:
            self.combo_rows.remove(edit)

        row_widget.setParent(None)
        row_widget.deleteLater()

        self.renumber_combo_rows()
        self.calculate_combo(silent=True)

    def renumber_combo_rows(self):
        for i in range(self.combo_layout.count()):
            widget = self.combo_layout.itemAt(i).widget()

            if widget:
                label = widget.findChild(QLabel)

                if label:
                    label.setText(f"Quote {i + 1}")

    def clear_combo_rows(self):
        for i in reversed(range(self.combo_layout.count())):
            item = self.combo_layout.takeAt(i)
            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.combo_rows.clear()

        self.combo_total_card.set_value("—")
        self.combo_return_card.set_value("—")
        self.combo_profit_card.set_value("—")

        self.add_combo_row()
        self.add_combo_row()

    def calculate_combo(self, silent=False):
        try:
            stake = dec(
                self.combo_stake.text(),
                "Einsatz"
            )

            if stake <= 0:
                raise ValueError(
                    "Der Einsatz muss größer 0 sein."
                )

            odds_list = []

            for i, field in enumerate(self.combo_rows, 1):

                if field.text().strip():
                    o = dec(
                        field.text(),
                        f"Quote {i}"
                    )

                    if o <= 1:
                        raise ValueError(
                            f"Quote {i} muss größer als 1 sein."
                        )

                    odds_list.append(o)

            if not odds_list:
                raise ValueError(
                    "Bitte mindestens eine Quote eingeben."
                )

            total_odds = D(1)

            for o in odds_list:
                total_odds *= o

            payout = stake * total_odds
            profit = payout - stake

            self.combo_total_card.set_value(
                odds_text(total_odds, 4)
            )

            self.combo_return_card.set_value(
                money(payout, self.currency)
            )

            self.combo_profit_card.set_value(
                money(profit, self.currency),
                "#38D9A9" if profit >= 0 else "#FF7272"
            )

        except ValueError as e:
            if not silent:
                self.show_error(str(e))

    # -------------------------------------------------
    # KAPITALMANAGER
    # -------------------------------------------------

    def update_start_capital(self):
        try:
            start = dec(
                self.start_capital_input.text(),
                "Startkapital"
            )

            if start < 0:
                raise ValueError(
                    "Das Startkapital darf nicht negativ sein."
                )

            self.starting_capital = start

            self.current_capital = (
                start
                + sum(
                    (D(str(x["result"])) for x in self.bet_history),
                    D(0)
                )
            )

            self.refresh_capital()

        except ValueError as e:
            self.show_error(str(e))

    def add_bet_result(self):
        try:
            start = dec(
                self.start_capital_input.text(),
                "Startkapital"
            )

            result = dec(
                self.bet_result_input.text(),
                "Nettoergebnis"
            )

            if start < 0:
                raise ValueError(
                    "Das Startkapital darf nicht negativ sein."
                )

            self.starting_capital = start

            description = (
                self.bet_description_input.text().strip()
                or "Abgeschlossene Wette"
            )

            record = {
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                ),
                "description": description,
                "result": str(result)
            }

            self.bet_history.append(record)

            self.current_capital = (
                self.starting_capital
                + sum(
                    (
                        D(str(x["result"]))
                        for x in self.bet_history
                    ),
                    D(0)
                )
            )

            self.bet_result_input.clear()
            self.bet_description_input.clear()

            self.refresh_capital()

        except ValueError as e:
            self.show_error(str(e))

    def delete_bet(self, index):
        if 0 <= index < len(self.bet_history):

            del self.bet_history[index]

            self.current_capital = (
                self.starting_capital
                + sum(
                    (
                        D(str(x["result"]))
                        for x in self.bet_history
                    ),
                    D(0)
                )
            )

            self.refresh_capital()

    def refresh_capital(self):
        total_profit = (
            self.current_capital - self.starting_capital
        )

        self.capital_card.set_value(
            money(self.current_capital, self.currency)
        )

        self.profit_card.set_value(
            money(total_profit, self.currency),
            "#38D9A9" if total_profit >= 0 else "#FF7272"
        )

        self.count_card.set_value(
            str(len(self.bet_history))
        )

        if hasattr(self, "start_capital_input"):
            self.start_capital_input.setText(
                str(self.starting_capital)
            )

        if not hasattr(self, "capital_table"):
            return

        self.capital_table.setRowCount(0)

        for i, entry in enumerate(self.bet_history):

            row = self.capital_table.rowCount()
            self.capital_table.insertRow(row)

            cumulative = (
                self.starting_capital
                + sum(
                    (
                        D(str(x["result"]))
                        for x in self.bet_history[:i + 1]
                    ),
                    D(0)
                )
            )

            dt = entry.get(
                "timestamp", ""
            ).replace("T", " ")

            result = D(str(entry["result"]))

            values = [
                dt,
                entry.get("description", ""),
                money(result, self.currency),
                money(cumulative, self.currency)
            ]

            for col, value in enumerate(values):
                self.capital_table.setItem(
                    row,
                    col,
                    self.table_item(value)
                )

            delete_btn = QPushButton("Löschen")

            delete_btn.clicked.connect(
                lambda checked=False, idx=i:
                self.delete_bet(idx)
            )

            self.capital_table.setCellWidget(
                row, 4, delete_btn
            )

        self.capital_summary.setText(
            f"Startkapital: "
            f"{money(self.starting_capital, self.currency)}"
            f"   ·   Bilanz: "
            f"{money(total_profit, self.currency)}"
            f"   ·   Aktuelles Kapital: "
            f"{money(self.current_capital, self.currency)}"
        )

    # -------------------------------------------------
    # WÄHRUNG
    # -------------------------------------------------

    def change_currency(self, currency):
        self.currency = currency

        self.refresh_capital()
        self.calculate_combo(silent=True)

    # -------------------------------------------------
    # JSON SPEICHERN
    # -------------------------------------------------

    def save_json(self):
        default_path = (
            Path(__file__).resolve().parent
            / "betting_analyzer_data.json"
        )

        # Speicherort und Dateinamen frei auswählbar.
        # Standardmäßig öffnet sich der Python-Ordner.
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Daten speichern – Speicherort und Dateiname wählen",
            str(default_path),
            "JSON-Dateien (*.json)"
        )

        if not path:
            return

        # Dateiendung automatisch ergänzen.
        if Path(path).suffix.lower() != ".json":
            path += ".json"

        data = {
            "version": 1,
            "currency": self.currency,
            "starting_capital": str(self.starting_capital),
            "bet_history": self.bet_history,

            "combo_stake": self.combo_stake.text(),
            "combo_odds": [
                x.text() for x in self.combo_rows
            ],

            "calculator_inputs": {
                "two_stake": self.two_stake.text(),
                "two_odds": self.two_odds.text(),
                "three_total": self.three_total.text(),
                "three_o1": self.three_o1.text(),
                "three_o2": self.three_o2.text(),
                "target_stake": self.target_stake.text(),
                "target_odds": self.target_odds.text()
            }
        }

        try:
            Path(path).write_text(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2
                ),
                encoding="utf-8"
            )

            QMessageBox.information(
                self,
                "Gespeichert",
                "Die Daten wurden erfolgreich als JSON gespeichert."
            )

        except OSError as e:
            self.show_error(
                f"Datei konnte nicht gespeichert werden:\n{e}"
            )

    # -------------------------------------------------
    # JSON LADEN
    # -------------------------------------------------

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Daten laden",
            str(Path(__file__).resolve().parent),
            "JSON-Dateien (*.json)"
        )

        if not path:
            return

        try:
            data = json.loads(
                Path(path).read_text(encoding="utf-8")
            )

            self.currency = data.get("currency", "€")

            idx = self.currency_box.findText(
                self.currency
            )

            if idx >= 0:
                self.currency_box.setCurrentIndex(idx)

            self.starting_capital = dec(
                data.get("starting_capital", "1000"),
                "Startkapital"
            )

            self.bet_history = data.get(
                "bet_history", []
            )

            self.current_capital = (
                self.starting_capital
                + sum(
                    (
                        D(str(x["result"]))
                        for x in self.bet_history
                    ),
                    D(0)
                )
            )

            self.combo_stake.setText(
                data.get("combo_stake", "")
            )

            inputs = data.get(
                "calculator_inputs", {}
            )

            self.two_stake.setText(
                inputs.get("two_stake", "")
            )
            self.two_odds.setText(
                inputs.get("two_odds", "")
            )
            self.three_total.setText(
                inputs.get("three_total", "")
            )
            self.three_o1.setText(
                inputs.get("three_o1", "")
            )
            self.three_o2.setText(
                inputs.get("three_o2", "")
            )
            self.target_stake.setText(
                inputs.get("target_stake", "")
            )
            self.target_odds.setText(
                inputs.get("target_odds", "")
            )

            self.clear_combo_rows()

            saved_odds = data.get(
                "combo_odds", []
            )

            if saved_odds:
                self.combo_rows[0].setText(
                    str(saved_odds[0])
                )

                for value in saved_odds[1:]:
                    self.add_combo_row(str(value))

            self.refresh_capital()
            self.calculate_combo(silent=True)

            QMessageBox.information(
                self,
                "Geladen",
                "Die Daten wurden erfolgreich geladen."
            )

        except (
            OSError,
            json.JSONDecodeError,
            ValueError,
            KeyError,
            TypeError
        ) as e:

            self.show_error(
                f"Die JSON-Datei konnte nicht geladen werden:\n{e}"
            )

    # -------------------------------------------------
    # ALLES ZURÜCKSETZEN
    # -------------------------------------------------

    def reset_data(self):
        answer = QMessageBox.question(
            self,
            "Zurücksetzen",
            "Möchtest du alle gespeicherten Kapitaldaten "
            "und Eingaben zurücksetzen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:
            return

        self.starting_capital = D("1000")
        self.current_capital = D("1000")
        self.bet_history = []

        self.start_capital_input.setText("1000")
        self.bet_result_input.clear()
        self.bet_description_input.clear()

        self.combo_stake.clear()
        self.clear_combo_rows()

        self.two_stake.clear()
        self.two_odds.clear()

        self.three_total.clear()
        self.three_o1.clear()
        self.three_o2.clear()

        self.target_stake.clear()
        self.target_odds.clear()

        self.hedge_table.setRowCount(0)

        self.hedge_result.setText(
            "Gib deine Werte ein und starte die Berechnung."
        )

        self.target_table.setRowCount(0)
        self.target_note.setText("Noch keine Berechnung.")

        self.refresh_capital()


# -------------------------------------------------
# PROGRAMMSTART
# -------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setFont(QFont("Segoe UI", 10))

    window = BettingAnalyzer()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()