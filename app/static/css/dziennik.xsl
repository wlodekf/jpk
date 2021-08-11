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
    	<th class="">Opis</th>
    	 
    	<th class="">Nr dow</th>
    	<th class="">Rodzaj dow</th>
    	 
		<th class="">Data operacji</th>
    	<th class="">Data dowodu</th> 
    	<th class="">Data ksieg</th>
    	
    	<th class="">Kod oper</th>  
    	<th class="">Opis oper</th>
    	<th class="kw">Kwota oper</th>
      </tr> 
         
      <xsl:for-each select="Dziennik">
      <tr>
		<td class="r"><xsl:apply-templates select="LpZapisuDziennika"/></td>
		<td class="r"><xsl:apply-templates select="NrZapisuDziennika"/></td>
    	<td class=""><xsl:apply-templates select="OpisDziennika"/></td>
    	 
    	<td class=""><xsl:apply-templates select="NrDowoduKsiegowego"/></td>
    	<td class=""><xsl:apply-templates select="RodzajDowodu"/></td> 
    	
		<td class=""><xsl:apply-templates select="DataOperacji"/></td>
    	<td class=""><xsl:apply-templates select="DataDowodu"/></td> 
    	<td class=""><xsl:apply-templates select="DataKsiegowania"/></td>
    	
    	<td class=""><xsl:apply-templates select="KodOperatora"/></td>
    	<td class=""><xsl:apply-templates select="OpisOperacji"/></td>
    	<td class="r"><xsl:apply-templates select="DziennikKwotaOperacji"/></td>
      </tr>     
      </xsl:for-each>         
   </table> 
     
</body>
</html>
</xsl:template>


<xsl:template match="Naglowek">
	<b>
		<xsl:apply-templates select="KodFormularza"/> (<xsl:apply-templates select="DataOd"/> - <xsl:apply-templates select="DataDo"/>)
		DZIENNIK KSIĘGOWAŃ				
	</b>
</xsl:template>


</xsl:stylesheet>