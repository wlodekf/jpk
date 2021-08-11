<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/informacja">
<html>
<head>
<LINK href="/css/info_wsa.css" rel="stylesheet" type="text/css"/>
<TITLE>
<xsl:value-of select="concat(substring(header_a/wartosc[1],22), ' - Informacja o sprawie')"/>
</TITLE>
</head>
<body>
   <xsl:apply-templates/> 
</body>
</html>
</xsl:template>

<xsl:template match="header_a">
   <div class="ha"><xsl:apply-templates/></div>
</xsl:template>

<xsl:template match="header_b/nazwa">
   <table class="hc" cellspacing="0" cellpadding="0"><tr>
      <td class="hcl nazwa"><xsl:apply-templates /></td>
      <td><xsl:value-of select="following-sibling::*[1]"/>
      </td>
   </tr></table>
</xsl:template>

<xsl:template match="header_b/wartosc">
</xsl:template>

<xsl:template match="header_c|header_d|header_e|header_f|header_g|footer_a|footer_b|details_a|group_header_1b|group_header_1c">
   <table class="hc" cellspacing="0" cellpadding="0"><tr>
      <td class="hcl"><xsl:apply-templates select="nazwa"/></td>
      <td><xsl:for-each select="wartosc">
             <xsl:apply-templates/><br/>
          </xsl:for-each>
      </td>
   </tr></table>
</xsl:template>

<xsl:template match="header_h">
   <div style="margin-top: 10px;">
   <h3><xsl:value-of select="wartosc"/></h3>
   <table cellspacing="0" cellpadding="0" style="width: 100%; background-color: #def;">
   <thead>
      <xsl:for-each select="row[1]/nazwa">
         <th><xsl:apply-templates/></th>
      </xsl:for-each>
   </thead>
      <xsl:for-each select="row">
         <tr>
            <xsl:for-each select="wartosc">
               <td class="ttd"><xsl:apply-templates/></td>
            </xsl:for-each>
         </tr>
      </xsl:for-each>
   </table>
   </div>
</xsl:template>

<xsl:template match="header_i/wartosc">
   <h3 class="hiw"><xsl:apply-templates/></h3>
</xsl:template>

<xsl:template match="group_header_1a">
   <div class="gh1a"><xsl:apply-templates/></div>
</xsl:template>

<xsl:template match="footer_a[1]">
   <h3 class="fa1"><xsl:value-of select="nazwa"/></h3>
   <xsl:for-each select="wartosc">
      <xsl:apply-templates/><br/>
   </xsl:for-each>
</xsl:template>

<xsl:template match="nazwa">
   <span class="nazwa">
      <xsl:apply-templates/>
   </span>
</xsl:template>

</xsl:stylesheet>