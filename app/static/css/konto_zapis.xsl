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
      
   <table class="dziennik" cellspacing="0" cellpadding="0">
      <tr>
		<th class="r">Lp</th>
		<th class="r">Lp dzi</th>
		
    	<th class="">Konto Wn</th>
    	<th class="kw">Kwota Wn</th>
    	<th class="">Opis Wn</th>
    	
  		<th class="">Konto Ma</th>
    	<th class="kw">Kwota Ma</th>
    	<th class="">Opis Ma</th>
      </tr> 
         
      <xsl:for-each select="KontoZapis">
      <tr>
		<td class="r"><xsl:apply-templates select="LpZapisu"/></td>
		<td class="r"><xsl:apply-templates select="NrZapisu"/></td>
		
    	<td class=""><xsl:apply-templates select="KodKontaWinien"/></td>
    	<td class=""><xsl:apply-templates select="KwotaWinien"/></td>
    	<td class=""><xsl:apply-templates select="OpisZapisuWinien"/></td> 
    	
    	<td class=""><xsl:apply-templates select="KodKontaMa"/></td>
    	<td class=""><xsl:apply-templates select="KwotaMa"/></td>
    	<td class=""><xsl:apply-templates select="OpisZapisuMa"/></td>     	
      </tr>     
      </xsl:for-each>         
   </table> 
     
</body>
</html>
</xsl:template>


<xsl:template match="Naglowek">
	<b>
		<xsl:apply-templates select="KodFormularza"/> (<xsl:apply-templates select="DataOd"/> - <xsl:apply-templates select="DataDo"/>)
		ZAPISY NA KONTACH				
	</b>
</xsl:template>


</xsl:stylesheet>