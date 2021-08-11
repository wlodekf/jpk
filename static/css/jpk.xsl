<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/JPK">
<html>
<head>
<TITLE><xsl:value-of select="kodFormularza"/></TITLE>
<LINK href="/static/css/xsl.css" rel="stylesheet" type="text/css"/>
</head>

<body>
   <xsl:apply-templates select="Naglowek"/>
      
   <table class="zois" cellspacing="0" cellpadding="0">
      <tr>
		<th class="st">Kod konta</th>
	
    	    	
		<th class="kw">BO Wn</th>
    	<th class="kw">BO Ma</th> 
    	<th class="kw">Okres Wn</th>
    	<th class="kw">Okres Ma</th> 
		<th class="kw">Nar Wn</th>
    	<th class="kw">Nar Ma</th> 
    	<th class="kw">Saldo Wn</th>
    	<th class="kw">Saldo Ma</th>  
    	
    	<th class="st">Opis konta</th>
    	<th class="st">Typ konta</th>
		<th class="st">Kod kategorii</th>
    	<th class="st">Opis kategorii</th>      	
		<th class="st">Kod zespolu</th>
    	<th class="st">Opis zespolu</th>   
    	 
      </tr> 
         
      <xsl:for-each select="ZOiS">
      <tr>
		<td class="st"><xsl:apply-templates select="KodKonta"/></td>
    	    	
		<td class="kw"><xsl:apply-templates select="BilansOtwarciaWinien"/></td>
    	<td class="kw"><xsl:apply-templates select="BilansOtwarciaMa"/></td> 
    	<td class="kw"><xsl:apply-templates select="ObrotyWinien"/></td>
    	<td class="kw"><xsl:apply-templates select="ObrotyMa"/></td> 
		<td class="kw"><xsl:apply-templates select="ObrotyWinienNarast"/></td>
    	<td class="kw"><xsl:apply-templates select="ObrotyMaNarast"/></td> 
    	<td class="kw"><xsl:apply-templates select="SaldoWinien"/></td>
    	<td class="kw"><xsl:apply-templates select="SaldoMa"/></td>
    	     	
    	<td class="st"><xsl:apply-templates select="OpisKonta"/></td>
    	<td class="st"><xsl:apply-templates select="TypKonta"/></td>
		<td class="st"><xsl:apply-templates select="KodKategorii"/></td>
    	<td class="st"><xsl:apply-templates select="OpisKategorii"/></td>       	
		<td class="st"><xsl:apply-templates select="KodZespolu"/></td>
    	<td class="st"><xsl:apply-templates select="OpisZespolu"/></td>    	
      </tr>     
      </xsl:for-each>         
   </table> 
     
</body>
</html>
</xsl:template>


<xsl:template match="Naglowek">
	<b><center>
		<xsl:apply-templates select="KodFormularza"/> (<xsl:apply-templates select="DataOd"/> - <xsl:apply-templates select="DataDo"/>)				
	</center></b>
</xsl:template>


</xsl:stylesheet>