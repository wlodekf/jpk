<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="text" encoding="utf-8"/>
<xsl:strip-space elements="*" />

<xsl:template match="/JPK">
Kod konta;BO Wn;BO Ma;Okres Wn;Okres Ma;Nar Wn;Nar Ma;Saldo Wn;Saldo Ma;Opis konta;Typ konta;Kod kategorii;Opis kategorii;Kod zespolu;Opis zespolu   
<xsl:for-each select="ZOiS">
<xsl:apply-templates select="KodKonta"/>;<xsl:apply-templates select="BilansOtwarciaWinien"/>;<xsl:apply-templates select="BilansOtwarciaMa"/>;<xsl:apply-templates select="ObrotyWinien"/>;<xsl:apply-templates select="ObrotyMa"/>;<xsl:apply-templates select="ObrotyWinienNarast"/>;<xsl:apply-templates select="ObrotyMaNarast"/>;<xsl:apply-templates select="SaldoWinien"/>;<xsl:apply-templates select="SaldoMa"/>;<xsl:apply-templates select="OpisKonta"/>;<xsl:apply-templates select="TypKonta"/>;<xsl:apply-templates select="KodKategorii"/>;<xsl:apply-templates select="OpisKategorii"/>;<xsl:apply-templates select="KodZespolu"/>;<xsl:apply-templates select="OpisZespolu"/><xsl:text>&#xD;</xsl:text>    	
</xsl:for-each>         
</xsl:template>

</xsl:stylesheet>