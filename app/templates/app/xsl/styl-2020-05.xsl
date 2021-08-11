<?xml version="1.0" encoding="UTF-8"?><xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:pf="http://crd.gov.pl/wzor/2020/05/08/{{jpk.pf}}/" version="1.0" xmlns:exsl="http://exslt.org/common" extension-element-prefixes="exsl">
	<xsl:import href="/static/css/Posredni_wspolne_v8-0E.xsl"/>
	<xsl:output method="html" encoding="UTF-8" indent="yes" version="4.01" doctype-public="-//W3C//DTD HTML 4.01//EN" doctype-system="http://www.w3.org/TR/html4/strict.dtd"/>
	<xsl:param name="nazwy-dla-kodow" select="true()"/>
	<xsl:param name="root" select="'{{root}}'"/>
 	<xsl:decimal-format name="pln" decimal-separator="," grouping-separator=" "/>
	<xsl:template name="TytulDokumentu">Jednolity plik kontrolny dla ewidencji w zakresie rozliczenia podatku należnego i naliczonego oraz deklaracji VAT-7</xsl:template>
	<xsl:template name="StyleDlaFormularza">
		<style type="text/css">
      .tlo-formularza { background-color:#D3D3D3; }
      		@media print {
	      		@page {
	     			size: A4 portrait;
					margin: 20px;
				}
				
    			table tbody tr {
        			page-break-inside: avoid;
    			}					
			}
    </style>
	</xsl:template>
	<xsl:template match="pf:JPK">
		<div class="jpk">
			<xsl:call-template name="NaglowekTechnicznyJPK">
				<xsl:with-param name="naglowek" select="pf:Naglowek"/>
				<xsl:with-param name="uzycie" select="'deklaracja'"/>
			</xsl:call-template>
			<xsl:call-template name="NaglowekTytulowy">
				<xsl:with-param name="uzycie" select="'deklaracja'"/>
				<xsl:with-param name="nazwa">
					<br/>
					<b>JEDNOLITY PLIK KONTROLNY</b>
					<br/>
					<br/>
				</xsl:with-param>
				<xsl:with-param name="objasnienie">
				</xsl:with-param>
			</xsl:call-template>
			<table class="normalna">
				<tr>
					<td class="wypelniane" style="width:50%">
						<div class="opisrubryki">Data i czas sporządzenia JPK_VAT</div>
						<xsl:apply-templates select="pf:Naglowek/pf:DataWytworzeniaJPK"/>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">Nazwa systemu, z którego pochodzą dane</div>
						<xsl:apply-templates select="pf:Naglowek/pf:NazwaSystemu"/>
					</td>
				</tr>
			</table>
			<xsl:call-template name="MiejsceICel">
				<xsl:with-param name="sekcja">A.</xsl:with-param>
			</xsl:call-template>
			<xsl:for-each select="pf:Podmiot1">
				<xsl:call-template name="Podmiot">
					<xsl:with-param name="sekcja">B.</xsl:with-param>
				</xsl:call-template>
				<table class="normalna">
					<tr>
						<xsl:if test="pf:OsobaFizyczna">
							<td class="wypelniane" style="width:50%">
								<div class="opisrubryki">Adres poczty elektronicznej</div>
								<xsl:apply-templates select="*[local-name()='OsobaFizyczna']/*[local-name() = 'Email']"/>
							</td>
							<td class="wypelniane">
								<div class="opisrubryki">Numer telefonu kontaktowego</div>
								<xsl:apply-templates select="*[local-name()='OsobaFizyczna']/*[local-name() = 'Telefon']"/>
							</td>
						</xsl:if>
						<xsl:if test="pf:OsobaNiefizyczna">
							<td class="wypelniane" style="width:50%">
								<div class="opisrubryki">Adres poczty elektronicznej</div>
								<xsl:apply-templates select="*[local-name()='OsobaNiefizyczna']/*[local-name() = 'Email']"/>
							</td>
							<td class="wypelniane">
								<div class="opisrubryki">Numer telefonu kontaktowego</div>
								<xsl:apply-templates select="*[local-name()='OsobaNiefizyczna']/*[local-name() = 'Telefon']"/>
							</td>
						</xsl:if>
					</tr>
				</table>
			</xsl:for-each>
			<xsl:if test="pf:Deklaracja">
				<xsl:for-each select="pf:Deklaracja">
					<xsl:call-template name="NaglowekTechnicznyDekl">
						<xsl:with-param name="naglowek" select="pf:Naglowek"/>
						<xsl:with-param name="uzycie" select="'deklaracja'"/>
					</xsl:call-template>
				</xsl:for-each>
				<xsl:call-template name="NaglowekTytulowy">
					<xsl:with-param name="naglowek" select="pf:Naglowek"/>
					<xsl:with-param name="uzycie" select="'deklaracja'"/>
					<xsl:with-param name="nazwa">
						<br/>
         DEKLARACJA DLA PODATKU OD TOWARÓW I USŁUG
        </xsl:with-param>
					<xsl:with-param name="objasnienie">
					</xsl:with-param>
				</xsl:call-template>
				<xsl:apply-templates select="pf:Deklaracja"/>
				<xsl:call-template name="PouczeniaKoncowe"/>
			</xsl:if>
			<xsl:if test="$root = ''">
			<xsl:if test="pf:Ewidencja">
				<xsl:call-template name="NaglowekEwidencja">
					<xsl:with-param name="uzycie" select="'deklaracja'"/>
					<xsl:with-param name="nazwa">
						<br/>EWIDENCJA PODATKU NALEŻNEGO I NALICZONEGO<br/>
					</xsl:with-param>
				</xsl:call-template>
				<xsl:call-template name="NaglowekTytulowyEwidencja">
					<xsl:with-param name="naglowek" select="pf:Naglowek"/>
					<xsl:with-param name="uzycie" select="'deklaracja'"/>
					<xsl:with-param name="nazwa">
						<br/>Ewidencja podatku należnego<br/>
					</xsl:with-param>
				</xsl:call-template>
				<xsl:for-each select="pf:Ewidencja">
					<xsl:call-template name="Sprzedaz"/>
				</xsl:for-each>
				<xsl:call-template name="NaglowekTytulowyEwidencja">
					<xsl:with-param name="naglowek" select="pf:Naglowek"/>
					<xsl:with-param name="uzycie" select="'deklaracja'"/>
					<xsl:with-param name="nazwa">
						<br/>Ewidencja podatku naliczonego<br/>
					</xsl:with-param>
				</xsl:call-template>
				<xsl:for-each select="pf:Ewidencja">
					<xsl:call-template name="Zakup"/>
				</xsl:for-each>
			</xsl:if>
			</xsl:if>			
		</div>
	</xsl:template>
	<xsl:template match="pf:Deklaracja">
		<xsl:call-template name="RozliczeniePodatkuNaleznego">
			<xsl:with-param name="sekcja">C.</xsl:with-param>
		</xsl:call-template>
		<xsl:call-template name="RozliczeniePodatkuNaliczonego">
			<xsl:with-param name="sekcja">D.</xsl:with-param>
		</xsl:call-template>
		<xsl:call-template name="ObliczenieZobowiązania">
			<xsl:with-param name="sekcja">E.</xsl:with-param>
		</xsl:call-template>
		<xsl:call-template name="InformacjeDodatkowe">
			<xsl:with-param name="sekcja">F.</xsl:with-param>
		</xsl:call-template>
	</xsl:template>
	<xsl:template name="RozliczeniePodatkuNaleznego">
		<xsl:param name="sekcja"/>
		<xsl:for-each select="pf:PozycjeSzczegolowe">
			<h2 class="tytul-sekcja-blok">
				<xsl:value-of select="$sekcja"/> ROZLICZENIE PODATKU NALEŻNEGO
      </h2>
			<table class="normalna">
				<td class="puste" style="width: 50%"/>
				<td class="niewypelniane" style="width:25%">Podstawa opodatkowania w zł</td>
				<td class="niewypelniane" style="width:25%">Podatek należny w zł</td>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania z tytułu dostawy towarów oraz świadczenia usług na terytorium kraju, zwolnionych od podatku</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_10</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_10)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="puste"/>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania z tytułu dostawy towarów oraz świadczenia usług poza terytorium kraju</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_11</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_11)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="puste"/>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania z tytułu świadczenia usług, o których mowa w art. 100 ust. 1 pkt 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_12</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_12)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="puste"/>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania z tytułu dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 0%</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_13</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_13)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="puste"/>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania z tytułu dostawy towarów, o której mowa w art. 129 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_14</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_14)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="puste"/>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania i podatku należnego z tytułu dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 5%, oraz korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_15</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_15)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_16</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_16)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania i podatku należnego z tytułu dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 7% albo 8%, oraz korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_17</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_17)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_18</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_18)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania i podatku należnego z tytułu dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 22% albo 23%, oraz korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_19</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_19)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_20</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_20)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania z tytułu wewnątrzwspólnotowej dostawy towarów</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_21</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_21)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="puste"/>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania z tytułu eksportu towarów</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_22</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_22)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="puste"/>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania i podatku należnego z tytułu wewnątrzwspólnotowego nabycia towarów</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_23</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_23)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_24</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_24)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania i podatku należnego z tytułu importu towarów rozliczanego zgodnie z art. 33a ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_25</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_25)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_26</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_26)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania i podatku należnego z tytułu importu usług, z wyłączeniem usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_27</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_27)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_28</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_28)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania i podatku należnego z tytułu importu usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_29</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_29)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_30</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_30)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania i podatku należnego z tytułu dostawy towarów, dla których podatnikiem jest nabywca zgodnie z art. 17 ust. 1 pkt 5 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_31</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_31)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_32</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_32)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</table>
			<table class="normalna">
				<tr>
					<td class="niewypelnianeopisy" style="width:75%">Wysokość podatku należnego od towarów objętych spisem z natury, o którym mowa w art. 14 ust. 5 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_33</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_33)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width:75%">Wysokość zwrotu odliczonej lub zwróconej kwoty wydanej na zakup kas rejestrujących, o którym mowa w art. 111 ust. 6 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_34</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_34)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width:75%">Wysokość podatku należnego od wewnątrzwspólnotowego nabycia środków transportu, wykazana w wysokości podatku należnego z tytułu określonego w P_24, podlegająca wpłacie w terminie, o którym mowa w art. 103 ust. 3, w związku z ust. 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_35</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_35)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width:75%">Wysokość podatku od wewnątrzwspólnotowego nabycia towarów, o których mowa w art. 103 ust. 5aa ustawy, podlegająca wpłacie w terminach, o których mowa w art. 103 ust. 5a i 5b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_36</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_36)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</table>
			<table class="normalna">
				<tr>
					<td class="niewypelnianeopisy" style="width:50%">
						<b>Łączna wysokość podstawy opodatkowania - P_37.</b> Suma kwot z P_10, P_11, P_13, P_15, P_17, P_19, P_21, P_22, P_23, P_25, P_27, P_29, P_31<br/>
						<b>Łączna wysokość podatku należnego - P_38.</b> Suma kwot z P_16, P_18, P_20, P_24, P_26, P_28, P_30, P_32, P_33, P_34 pomniejszona o kwotę z P_35 i P_36</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_37</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_37)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_38</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_38)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</table>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="RozliczeniePodatkuNaliczonego">
		<xsl:param name="sekcja"/>
		<xsl:for-each select="pf:PozycjeSzczegolowe">
			<h2 class="tytul-sekcja-blok">
				<xsl:value-of select="$sekcja"/> ROZLICZENIE PODATKU NALICZONEGO
      </h2>
			<h3 class="tytul-sekcja-blok">
				<xsl:value-of select="$sekcja"/>1. PRZENIESIENIA
      </h3>
			<table class="normalna">
				<td class="puste" style="width: 75%"/>
				<td class="niewypelniane" style="width:25%">Podatek do odliczenia w zł</td>
				<tr>
					<td class="niewypelnianeopisy">Wysokość nadwyżki podatku naliczonego nad należnym z poprzedniej deklaracji</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_39</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_39)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</table>
			<h3 class="tytul-sekcja-blok">
				<xsl:value-of select="$sekcja"/>2. NABYCIE TOWARÓW I USŁUG ORAZ PODATEK NALICZONY Z UWZGLĘDNIENIEM KOREKT
      </h3>
			<table class="normalna">
				<td class="puste" style="width: 50%"/>
				<td class="niewypelniane" style="width:25%">Wartość netto w zł</td>
				<td class="niewypelniane" style="width:25%">Podatek naliczony w zł</td>
				<tr>
					<td class="niewypelnianeopisy">Wartość netto oraz wysokość podatku naliczonego z tytułu nabycia towarów i usług zaliczanych u podatnika do środków trwałych</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_40</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_40)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_41</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_41)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy">Wartość netto oraz wysokość podatku naliczonego z tytułu nabycia pozostałych towarów i usług</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_42</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_42)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_43</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_43)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</table>
			<h3 class="tytul-sekcja-blok">
				<xsl:value-of select="$sekcja"/>3. PODATEK NALICZONY - DO ODLICZENIA <span style="text-transform:lowercase">(w zł)</span>
			</h3>
			<table class="normalna">
				<td class="niewypelnianeopisy" style="width: 75%">Wysokość podatku naliczonego z tytułu korekty podatku naliczonego od nabycia towarów i usług zaliczanych u podatnika do środków trwałych</td>
				<td class="wypelniane">
					<div class="opisrubryki">P_44</div>
					<div class="kwota">
						<xsl:call-template name="TransformataKwoty">
							<xsl:with-param name="kwota" select="string(pf:P_44)"/>
							<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
						</xsl:call-template>
					</div>
				</td>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Wysokość podatku naliczonego z tytułu korekty podatku naliczonego od nabycia pozostałych towarów i usług</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_45</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_45)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Wysokość podatku naliczonego z tytułu korekty podatku naliczonego, o której mowa w art. 89b ust. 1 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_46</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_46)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Wysokość podatku naliczonego z tytułu korekty podatku naliczonego, o której mowa w art. 89b ust. 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_47</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_47)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">
						<b>Łączna wysokość podatku naliczonego do odliczenia.</b> Suma kwot z P_39, P_41, P_43, P_44, P_45, P_46 i P_47</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_48</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_48)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</table>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="ObliczenieZobowiązania">
		<xsl:param name="sekcja"/>
		<xsl:for-each select="pf:PozycjeSzczegolowe">
			<h2 class="tytul-sekcja-blok">
				<xsl:value-of select="$sekcja"/> OBLICZENIE WYSOKOŚCI ZOBOWIĄZANIA PODATKOWEGO LUB KWOTY ZWROTU <span style="text-transform:lowercase">(w zł)</span>
			</h2>
			<table class="normalna">
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Kwota wydana na zakup kas rejestrujących, do odliczenia w danym okresie rozliczeniowym pomniejszająca wysokość podatku należnego</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_49</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_49)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Wysokość podatku objęta zaniechaniem poboru</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_50</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_50)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Wysokość podatku podlegająca wpłacie do urzędu skarbowego</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_51</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_51)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Kwota wydana na zakup kas rejestrujących, do odliczenia w danym okresie rozliczeniowym przysługująca do zwrotu w danym okresie rozliczeniowym lub powiększająca wysokość podatku naliczonego do przeniesienia na następny okres rozliczeniowy</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_52</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_52)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Wysokość nadwyżki podatku naliczonego nad należnym</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_53</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_53)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Wysokość nadwyżki podatku naliczonego nad należnym do zwrotu na rachunek wskazany przez podatnika</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_54</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_54)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</table>
			<table class="normalna">
				<tr>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_55 Zwrot na rachunek VAT, o którym mowa w art. 87 ust. 6a ustawy</div>
						<xsl:if test="pf:P_55 ='1'">
							<div class="kwota">
								<p style="text-align: center">
									<input type="checkbox" checked="checked" disabled="disabled"/> tak
							</p>
							</div>
						</xsl:if>
					</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_56 Zwrot w terminie, o którym mowa w art. 87 ust. 6 ustawy</div>
						<xsl:if test="pf:P_56 ='1'">
							<p style="text-align: center">
								<input type="checkbox" checked="checked" disabled="disabled"/> tak
							</p>
						</xsl:if>
					</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_57 Zwrot w terminie, o którym mowa w art. 87 ust. 2 ustawy</div>
						<xsl:if test="pf:P_57 ='1'">
							<p style="text-align: center">
								<input type="checkbox" checked="checked" disabled="disabled"/> tak
							</p>
						</xsl:if>
					</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_58 Zwrot w terminie, o którym mowa w art. 87 ust. 5a zdanie pierwsze ustawy</div>
						<xsl:if test="pf:P_58 ='1'">
							<p style="text-align: center">
								<input type="checkbox" checked="checked" disabled="disabled"/> tak
							</p>
						</xsl:if>
					</td>
				</tr>
			</table>
			<table class="normalna">
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Zaliczenie zwrotu podatku na poczet przyszłych zobowiązań podatkowych</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_59</div>
						<p style="text-align: center">
							<xsl:if test="pf:P_59 ='1'">
								<p style="text-align: center">
									<input type="checkbox" checked="checked" disabled="disabled"/> tak
							</p>
							</xsl:if>
						</p>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Wysokość zwrotu do zaliczenia na poczet przyszłych zobowiązań podatkowych</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_60</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_60)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="niewypelnianeopisy" style="width: 75%">Rodzaj przyszłego zobowiązania podatkowego</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_61</div>
						<div class="kwota">
							<xsl:value-of select="pf:P_61"/>
						</div>
					</td>
				</tr>
			</table>
			<table class="normalna">
				<tr>
					<td class="niewypelnianeopisy" style="width:75%">Wysokość nadwyżki podatku naliczonego nad należnym do przeniesienia na następny okres rozliczeniowy</td>
					<td class="wypelniane" style="width:25%">
						<div class="opisrubryki">P_62</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_62)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</table>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="InformacjeDodatkowe">
		<xsl:param name="sekcja"/>
		<xsl:for-each select="pf:PozycjeSzczegolowe">
			<h2 class="tytul-sekcja-blok">
				<xsl:value-of select="$sekcja"/> INFORMACJE DODATKOWE
      </h2>
			<table class="normalna">
				<tr>
					<td class="niewypelnianeopisy" style="width: 20%">Podatnik wykonywał w okresie rozliczeniowym czynności, o których mowa w:</td>
					<xsl:if test="pf:P_63 ='1'">
						<td class="wypelniane">
							<div class="opisrubryki">P_63</div>
							<input type="checkbox" checked="checked" disabled="disabled"/>art. 119 ustawy
            </td>
					</xsl:if>
					<xsl:if test="pf:P_64 ='1'">
						<td class="wypelniane">
							<div class="opisrubryki">P_64</div>
							<input type="checkbox" checked="checked" disabled="disabled"/>art. 120 ust. 4 lub 5 ustawy
            </td>
					</xsl:if>
					<xsl:if test="pf:P_65 ='1'">
						<td class="wypelniane">
							<div class="opisrubryki">P_65</div>
							<input type="checkbox" checked="checked" disabled="disabled"/>art. 122 ustawy
            </td>
					</xsl:if>
					<xsl:if test="pf:P_66 ='1'">
						<td class="wypelniane">
							<div class="opisrubryki">P_66</div>
							<input type="checkbox" checked="checked" disabled="disabled"/>art. 136 ustawy
            </td>
					</xsl:if>
				</tr>
			</table>
			<table class="normalna">
				<tr>
					<td class="wypelniane">
						<div class="opisrubryki">P_67 Podatnik korzysta z obniżenia zobowiązania podatkowego, o którym mowa w art. 108d ustawy</div>
						<p style="text-align: center">
							<xsl:if test="pf:P_67 ='1'">
								<input type="checkbox" checked="checked" disabled="disabled"/>tak
              </xsl:if>
						</p>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_68 Wysokość korekty podstawy opodatkowania, o której mowa w art. 89a ust. 1 ustawy</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_68)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
					<td class="wypelniane">
						<div class="opisrubryki">P_69 Wysokość korekty podatku należnego, o której mowa w art. 89a ust. 1 ustawy</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:P_69)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="1"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
				<tr>
					<td class="wypelniane" colspan="3">
						<div class="opisrubryki">P_ORDZU Uzasadnienie przyczyn złożenia korekty</div>
						<xsl:value-of select="pf:P_ORDZU"/>
					</td>
				</tr>
			</table>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="Sprzedaz">
		<xsl:param name="sekcja"/>
		<xsl:for-each select="pf:SprzedazWiersz">
			<table>
				<tr>
					<td class="tytul-sekcja-blok" style="text-transform: none; font-weight: bold; font-size: 1.3em; ">
							Lp. wiersza ewidencji - <span style="font-size: 1.5em;">
							<xsl:value-of select="pf:LpSprzedazy"/>
						</span>
					</td>
				</tr>
			</table>
			<xsl:call-template name="EwidencjaPodatkuNaleznego">
				<xsl:with-param name="sekcja">
					<xsl:value-of select="$sekcja"/>
				</xsl:with-param>
			</xsl:call-template>
		</xsl:for-each>
		<xsl:for-each select="pf:SprzedazCtrl">
			<xsl:call-template name="EwidencjaPodatkuNaleznegoSuma">
			</xsl:call-template>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="EwidencjaPodatkuNaleznego">
		<table class="normalna">
			<tr>
				<td class="wypelniane" style="width: 20%">
					<div class="opisrubryki">Kod kraju nadania numeru, za pomocą którego nabywca, dostawca lub usługodawca jest zidentyfikowany na potrzeby podatku lub podatku od wartości dodanej</div>
					<div>
						<xsl:apply-templates select="pf:KodKrajuNadaniaTIN"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 30%">
					<div class="opisrubryki">Numer, za pomocą którego nabywca, dostawca lub usługodawca jest zidentyfikowany na potrzeby podatku lub podatku od wartości dodanej (wyłącznie kod cyfrowo-literowy)</div>
					<div>
						<xsl:value-of select="pf:NrKontrahenta"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 50%">
					<div class="opisrubryki">Imię i nazwisko lub nazwa nabywcy, dostawcy lub usługodawcy</div>
					<div>
						<xsl:value-of select="pf:NazwaKontrahenta"/>
					</div>
				</td>
			</tr>
		</table>
		<table class="normalna">
			<tr>
				<td class="wypelniane" style="width: 30%">
					<div class="opisrubryki">Numer dowodu</div>
					<div>
						<xsl:value-of select="pf:DowodSprzedazy"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 20%">
					<div class="opisrubryki">Data wystawienia dowodu</div>
					<div>
						<xsl:value-of select="pf:DataWystawienia"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 20%">
					<div class="opisrubryki">Data dokonania lub zakończenia dostawy towarów lub wykonania usługi lub data otrzymania zapłaty, o której mowa w art. 106b ust. 1 pkt 4 ustawy, o ile taka data jest określona i różni się od daty wystawienia dowodu. W przeciwnym przypadku - pole puste</div>
					<div>
						<xsl:value-of select="pf:DataSprzedazy"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 30%">
					<div class="opisrubryki">Oznaczenie dowodu sprzedaży</div>
					<div>
						<xsl:choose>
							<xsl:when test="pf:TypDokumentu ='RO'">
                RO - Dokument zbiorczy wewnętrzny zawierający sprzedaż z kas rejestrujących
              </xsl:when>
							<xsl:when test="pf:TypDokumentu ='WEW'">
                WEW - Dokument wewnętrzny
              </xsl:when>
							<xsl:when test="pf:TypDokumentu ='FP'">
                FP - Faktura, o której mowa w art. 109 ust. 3d ustawy
              </xsl:when>
						</xsl:choose>
					</div>
				</td>
			</tr>
		</table>
		<table class="normalna">
			<tr>
				<td class="niewypelniane" style="width: 50%">Oznaczenie dotyczące dostawy i świadczenia usług</td>
				<td class="niewypelniane" style="width: 50%">Oznaczenia dotyczące procedur</td>
			</tr>
			<tr>
				<td class="wypelniane" style="width: 50%">
					<xsl:if test="pf:GTU_01 ='1'">
						GTU_01
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_02 ='1'">
						GTU_02
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_03 ='1'">
						GTU_03
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_04 ='1'">
						GTU_04
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_05 ='1'">
						GTU_05
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_06 ='1'">
						GTU_06
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_07 ='1'">
						GTU_07
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_08 ='1'">
						GTU_08
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_09='1'">
						GTU_09
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_10 ='1'">
						GTU_10
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_11 ='1'">
						GTU_11
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_12 ='1'">
						GTU_12
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:GTU_13 ='1'">
						GTU_13
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
				</td>
				<td class="wypelniane" style="width: 50%">
					<xsl:if test="pf:SW ='1'">
						SW
						<input type="checkbox" checked="checked" disabled="disabled"/>,</xsl:if>
					<xsl:if test="pf:EE ='1'">
						EE
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:TP ='1'">
						TP
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:TT_WNT ='1'">
						TT_WNT
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:TT_D ='1'">
						TT_D
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:MR_T ='1'">
						MR_T
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:MR_UZ ='1'">
						MR_UZ
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:I_42 ='1'">
						I_42
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:I_63 ='1'">
						I_63
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:B_SPV ='1'">
						B_SPV
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:B_SPV_DOSTAWA ='1'">
						B_SPV_DOSTAWA
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:B_MPV_PROWIZJA ='1'">
						B_MPV_PROWIZJA
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
					<xsl:if test="pf:MPP ='1'">
						MPP
						<input type="checkbox" checked="checked" disabled="disabled"/>,
            </xsl:if>
				</td>
			</tr>
		</table>
		<table class="normalna">
			<tr>
				<td class="niewypelnianeopisy">Korekta podstawy opodatkowania oraz podatku należnego, o której mowa w art. 89a ust. 1 i 4 ustawy</td>
				<td class="wypelniane">
					<p style="text-align: center">
						<xsl:if test="pf:KorektaPodstawyOpodt ='1'">
							<input type="checkbox" checked="checked" disabled="disabled"/>tak
            </xsl:if>
					</p>
				</td>
			</tr>
		</table>
		<table class="normalna">
			<tr>
				<td class="puste"/>
				<td class="niewypelniane" style="text-align: center; width: 25%">Kwota</td>
			</tr>
			<xsl:if test=".//pf:K_10">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z dostawy towarów oraz świadczenia usług na terytorium kraju, zwolnionych od podatku</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_10</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_10)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_11">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z dostawy towarów oraz świadczenia usług poza terytorium kraju</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_11</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_11)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_12">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca ze świadczenia usług, o których mowa w art. 100 ust. 1 pkt 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_12</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_12)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_13">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 0%</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_13</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_13)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_14">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z dostawy towarów, o której mowa w art. 129 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_14</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_14)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_15">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 5%, z uwzględnieniem korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_15</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_15)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_16">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego wynikająca z dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 5%, z uwzględnieniem korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_16</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_16)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_17">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 7% albo 8%, z uwzględnieniem korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_17</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_17)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_18">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego wynikająca z dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 7% albo 8%, z uwzględnieniem korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_18</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_18)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_19">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 22% albo 23%, z uwzględnieniem korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_19</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_19)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_20">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego wynikająca z dostawy towarów oraz świadczenia usług na terytorium kraju, opodatkowanych stawką 22% albo 23%, z uwzględnieniem korekty dokonanej zgodnie z art. 89a ust. 1 i 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_20</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_20)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_21">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z wewnątrzwspólnotowej dostawy towarów, o której mowa w art. 13 ust. 1 i 3 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_21</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_21)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_22">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z eksportu towarów</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_22</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_22)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_23">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z wewnątrzwspólnotowego nabycia towarów</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_23</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_23)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_24">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego wynikająca z wewnątrzwspólnotowego nabycia towarów</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_24</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_24)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_25">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z importu towarów rozliczanego zgodnie z art. 33a ustawy, potwierdzona zgłoszeniem celnym lub deklaracją importową, o której mowa w art. 33b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_25</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_25)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_26">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego wynikająca z importu towarów rozliczanego zgodnie z art. 33a ustawy, potwierdzona zgłoszeniem celnym lub deklaracją importową, o której mowa w art. 33b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_26</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_26)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_27">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z importu usług, z wyłączeniem usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_27</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_27)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_28">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego wynikająca z importu usług, z wyłączeniem usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_28</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_28)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_29">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z importu usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_29</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_29)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_30">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego wynikająca z importu usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_30</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_30)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_31">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podstawy opodatkowania wynikająca z dostawy towarów, dla których podatnikiem jest nabywca zgodnie z art. 17 ust. 1 pkt 5 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_31</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_31)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_32">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego wynikająca z dostawy towarów, dla których podatnikiem jest nabywca zgodnie z art. 17 ust. 1 pkt 5 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_32</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_32)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_33">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego od towarów objętych spisem z natury, o którym mowa w art. 14 ust. 5 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_33</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_33)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_34">
				<tr>
					<td class="niewypelnianeopisy">Wysokość zwrotu odliczonej lub zwróconej kwoty wydanej na zakup kas rejestrujących, o którym mowa w art. 111 ust. 6 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_34</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_34)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_35">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego od wewnątrzwspólnotowego nabycia środków transportu, wykazana w wysokości podatku należnego z tytułu wewnątrzwspólnotowego nabycia towarów, podlegająca wpłacie w terminie, o którym mowa w art. 103 ust. 3, w związku z ust. 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_35</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_35)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_36">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku należnego od wewnątrzwspólnotowego nabycia towarów, o których mowa w art. 103 ust. 5aa ustawy, podlegająca wpłacie w terminie, o którym mowa w art. 103 ust. 5a i 5b ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_36</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_36)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:SprzedazVAT_Marza">
				<tr>
					<td class="niewypelnianeopisy">Wartość sprzedaży brutto dostawy towarów i świadczenia usług opodatkowanych na zasadach marży zgodnie z art. 119 i art. 120 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">SprzedazVAT_Marza</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:SprzedazVAT_Marza)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
		</table>
	</xsl:template>
	<xsl:template name="EwidencjaPodatkuNaleznegoSuma">
		<xsl:param name="sekcja"/>
		<xsl:param name="pozycja"/>
		<h3 class="tytul-sekcja-blok">
			<xsl:value-of select="$pozycja"/>
	SUMA PODATKU NALEŻNEGO
		</h3>
		<table class="normalna">
			<tr>
				<td class="niewypelnianeopisy" style="width: 75%">
					<b>Liczba wierszy ewidencji w zakresie rozliczenia podatku należnego, w okresie którego dotyczy JPK.</b>
					<br/> Jeżeli ewidencja nie zawiera wierszy należy wykazać 0</td>
				<td class="wypelniane">
					<br/>
					<div class="kwota">
						<xsl:value-of select="pf:LiczbaWierszySprzedazy"/>
					</div>
				</td>
			</tr>
			<tr>
				<td class="niewypelnianeopisy">
					<b>Podatek należny według ewidencji w okresie, którego dotyczy JPK.</b>
					<br/> Suma kwot z K_16, K_18, K_20, K_24, K_26, K_28, K_30, K_32, K_33 i K_34 pomniejszona o kwotę z K_35 i K_36, z wyłączeniem faktur, o których mowa w art. 109 ust. 3d ustawy (oznaczonych FP).<br/> Jeżeli w ewidencji nie wypełniono żadnego ze wskazanych elementów, wówczas należy wykazać 0.00</td>
				<td class="wypelniane">
					<br/>
					<div class="kwota">
						<xsl:call-template name="TransformataKwoty">
							<xsl:with-param name="kwota" select="string(pf:PodatekNalezny)"/>
							<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
						</xsl:call-template>
					</div>
				</td>
			</tr>
		</table>
	</xsl:template>
	<xsl:template name="Zakup">
		<xsl:param name="sekcja"/>
		<xsl:for-each select="pf:ZakupWiersz">
			<xsl:call-template name="EwidencjaPodatkuNaliczonego">
				<xsl:with-param name="sekcja">
					<xsl:value-of select="$sekcja"/>
				</xsl:with-param>
				<xsl:with-param name="pozycja" select="position()"/>
			</xsl:call-template>
		</xsl:for-each>
		<xsl:for-each select="pf:ZakupCtrl">
			<xsl:call-template name="EwidencjaPodatkuNaliczonegoSuma">
			</xsl:call-template>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="EwidencjaPodatkuNaliczonegoNaglowek">
		<xsl:param name="sekcja"/>
		<h2 class="tytul-sekcja-blok">
			<xsl:value-of select="$sekcja"/> EWIDENJCA PODATKU NALICZONEGO
    </h2>
	</xsl:template>
	<xsl:template name="EwidencjaPodatkuNaliczonego">
		<xsl:param name="sekcja"/>
		<xsl:param name="pozycja"/>
		<table>
			<tr>
				<td class="tytul-sekcja-blok" style="text-transform: none; font-weight: bold; font-size: 1.3em; ">
							Lp. wiersza ewidencji - <span style="font-size: 1.5em;">
						<xsl:value-of select="pf:LpZakupu"/>
					</span>
				</td>
			</tr>
		</table>
		<table class="normalna">
			<tr>
				<td class="wypelniane" style="width: 20%">
					<div class="opisrubryki">Kod kraju nadania numeru, za pomocą którego dostawca lub usługodawca jest zidentyfikowany na potrzeby podatku lub podatku od wartości dodanej</div>
					<div>
						<xsl:apply-templates select="pf:KodKrajuNadaniaTIN"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 30%">
					<div class="opisrubryki"> Numer, za pomocą którego dostawca lub usługodawca jest zidentyfikowany na potrzeby podatku lub podatku od wartości dodanej (wyłącznie kod cyfrowo-literowy)</div>
					<div>
						<xsl:value-of select="pf:NrDostawcy"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 50%">
					<div class="opisrubryki"> Imię i nazwisko lub nazwa dostawcy lub usługodawcy</div>
					<div>
						<xsl:value-of select="pf:NazwaDostawcy"/>
					</div>
				</td>
			</tr>
		</table>
		<table class="normalna">
			<tr>
				<td class="wypelniane" style="width: 20%">
					<div class="opisrubryki">Numer dowodu zakupu</div>
					<div>
						<xsl:value-of select="pf:DowodZakupu"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 10%">
					<div class="opisrubryki"> Data wystawienia dowodu zakupu</div>
					<div>
						<xsl:value-of select="pf:DataZakupu"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 10%">
					<div class="opisrubryki">Data wpływu dowodu zakupu</div>
					<div>
						<xsl:value-of select="pf:DataWplywu"/>
					</div>
				</td>
				<td class="wypelniane" style="width: 30%">
					<div class="opisrubryki">Oznaczenie dowodu zakupu</div>
					<div>
						<xsl:choose>
							<xsl:when test="pf:DokumentZakupu ='MK'">
                MK - Faktura wystawiona przez podatnika będącego dostawcą lub usługodawcą, który wybrał metodę kasową rozliczeń określoną w art. 21 ustawy
              </xsl:when>
							<xsl:when test="pf:DokumentZakupu ='VAT_RR'">
                VAT_RR - Faktura VAT RR, o której mowa w art. 116 ustawy
              </xsl:when>
							<xsl:when test="pf:DokumentZakupu ='WEW'">
                WEW - Dokument wewnętrzny
              </xsl:when>
						</xsl:choose>
					</div>
				</td>
				<td class="wypelniane" style="width: 20%">
					<div class="opisrubryki">Transakcja objęta obowiązkiem stosowania mechanizmu podzielonej płatności</div>
					<p style="text-align: center">
						<xsl:if test="pf:MPP ='1'">
							MPP<input type="checkbox" checked="checked" disabled="disabled"/>tak
            </xsl:if>
					</p>
				</td>
				<td class="wypelniane" style="width: 20%">
					<div class="opisrubryki">Oznaczenie dotyczące podatku naliczonego z tytułu importu towarów, w tym importu towarów rozliczanego zgodnie z art. 33a ustawy</div>
					<p style="text-align: center">
						<xsl:if test="pf:IMP ='1'">
							IMP<input type="checkbox" checked="checked" disabled="disabled"/>tak
            </xsl:if>
					</p>
				</td>
			</tr>
		</table>
		<table class="normalna">
			<tr>
				<td class="puste"/>
				<td class="niewypelniane" style="text-align: center; width: 25%">Kwota</td>
			</tr>
			<xsl:if test=".//pf:K_40">
				<tr>
					<td class="niewypelnianeopisy">Wartość netto wynikająca z nabycia towarów i usług zaliczanych u podatnika do środków trwałych</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_40</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_40)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_41">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku naliczonego przysługująca do odliczenia z podstaw określonych w art. 86 ust. 2 ustawy, na warunkach określonych w ustawie wynikająca z nabycia towarów i usług zaliczanych u podatnika do środków trwałych</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_41</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_41)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_42">
				<tr>
					<td class="niewypelnianeopisy">Wartość netto wynikająca z nabycia pozostałych towarów i usług</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_42</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_42)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_43">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku naliczonego przysługująca do odliczenia z podstaw określonych w art. 86 ust. 2 ustawy, na warunkach określonych w ustawie wynikająca z nabycia pozostałych towarów i usług</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_43</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_43)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_44">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku naliczonego wynikająca z korekt podatku naliczonego, o których mowa w art. 90a-90c oraz art. 91 ustawy, z tytułu nabycia towarów i usług zaliczanych u podatnika do środków trwałych</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_44</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_44)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_45">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku naliczonego wynikająca z korekt podatku naliczonego, o których mowa w art. 90a-90c oraz art. 91 ustawy, z tytułu nabycia pozostałych towarów i usług</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_45</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_45)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_46">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku naliczonego wynikająca z korekty podatku naliczonego, o której mowa w art. 89b ust. 1 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_46</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_46)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:K_47">
				<tr>
					<td class="niewypelnianeopisy">Wysokość podatku naliczonego wynikająca z korekty podatku naliczonego, o której mowa w art. 89b ust. 4 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">K_47</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:K_47)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test=".//pf:ZakupVAT_Marza">
				<tr>
					<td class="niewypelnianeopisy">Kwota nabycia towarów i usług nabytych od innych podatników dla bezpośredniej korzyści turysty, a także nabycia towarów używanych, dzieł sztuki, przedmiotów kolekcjonerskich i antyków związanych ze sprzedażą opodatkowaną na zasadzie marży zgodnie z art. 120 ustawy</td>
					<td class="wypelniane">
						<div class="opisrubryki">ZakupVAT_Marza</div>
						<div class="kwota">
							<xsl:call-template name="TransformataKwoty">
								<xsl:with-param name="kwota" select="string(pf:ZakupVAT_Marza)"/>
								<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
							</xsl:call-template>
						</div>
					</td>
				</tr>
			</xsl:if>
		</table>
	</xsl:template>
	<xsl:template name="EwidencjaPodatkuNaliczonegoSuma">
		<xsl:param name="sekcja"/>
		<xsl:param name="pozycja"/>
		<h3 class="tytul-sekcja-blok">
			<xsl:value-of select="$pozycja"/>
		SUMA PODATKU NALICZONEGO
		</h3>
		<table class="normalna">
			<tr>
				<td class="niewypelnianeopisy" style="width: 75%">
					<b>Liczba wierszy ewidencji w zakresie rozliczenia podatku naliczonego, w okresie którego dotyczy JPK.</b>
					<br/> Jeżeli ewidencja nie zawiera wierszy należy wykazać 0</td>
				<td class="wypelniane">
					<div class="kwota">
						<xsl:value-of select="pf:LiczbaWierszyZakupow"/>
					</div>
				</td>
			</tr>
			<tr>
				<td class="niewypelnianeopisy">
					<b>Razem kwota podatku naliczonego do odliczenia</b>
					<br/>Suma kwot z K_41, K_43, K_44, K_45, K_46, K_47. <br/>Jeżeli w ewidencji nie wypełniono żadnego ze wskazanych elementów, wówczas należy wykazać 0.00</td>
				<td class="wypelniane">
					<br/>
					<div class="kwota">
						<xsl:call-template name="TransformataKwoty">
							<xsl:with-param name="kwota" select="string(pf:PodatekNaliczony)"/>
							<xsl:with-param name="czyKwotaZaokraglona" select="0"/>
						</xsl:call-template>
					</div>
				</td>
			</tr>
		</table>
	</xsl:template>
	<xsl:template name="TransformataKwoty">
		<xsl:param name="kwota"/>
		<xsl:param name="czyKwotaZaokraglona"/>
		<xsl:choose>
			<xsl:when test="$kwota = ''">
				<xsl:choose>
					<xsl:when test="$czyKwotaZaokraglona">
            <!-- zł -->
          </xsl:when>
					<xsl:otherwise>
            zł,   gr
          </xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<xsl:when test="contains($kwota, '.')">
				<xsl:value-of select="format-number(substring-before($kwota,'.'), '# ##0', 'pln')"/> zł, <xsl:value-of select="substring-after($kwota,'.')"/> gr
      </xsl:when>
			<xsl:otherwise>
				<xsl:choose>
					<xsl:when test="$czyKwotaZaokraglona">
						<xsl:value-of select="format-number($kwota, '# ##0', 'pln')"/> <!-- zł -->
          </xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="$kwota"/> zł, 00 gr
          </xsl:otherwise>
				</xsl:choose>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="NaglowekTechnicznyDekl">
		<xsl:param name="uzycie"/>
		<xsl:param name="naglowek"/>
		<xsl:param name="alternatywny-naglowek" select="$naglowek"/>
		<xsl:variable name="kod" select="$naglowek/*[local-name()='KodFormularzaDekl']"/>
		<xsl:variable name="kod2" select="$alternatywny-naglowek/*[local-name()='KodFormularzaDekl']"/>
		<xsl:variable name="wariant" select="$naglowek/*[local-name()='WariantFormularzaDekl']"/>
		<div class="naglowek">
			<table>
				<tr>
					<td colspan="2">
						<span class="kod-formularza">
							<xsl:apply-templates select="$kod"/>
						</span>
						<xsl:text> </xsl:text>
						<span class="wariant">(<xsl:apply-templates select="$wariant"/>)</span>
					</td>
				</tr>
				<tr>
					<td class="etykieta">Kod systemowy</td>
					<td class="wartosc">
						<xsl:value-of select="$kod/@kodSystemowy"/>
					</td>
				</tr>
				<xsl:call-template name="AtrybutNaglowka">
					<xsl:with-param name="etykieta">Kod podatku</xsl:with-param>
					<xsl:with-param name="pierwszy" select="$kod/@kodPodatku"/>
					<xsl:with-param name="drugi" select="$kod2/@kodPodatku"/>
				</xsl:call-template>
			</table>
		</div>
	</xsl:template>
	<xsl:template name="NaglowekTechnicznyJPK">
		<xsl:param name="uzycie"/>
		<!-- deklaracja | zalacznik -->
		<xsl:param name="naglowek"/>
		<xsl:param name="alternatywny-naglowek" select="$naglowek"/>
		<xsl:variable name="kod" select="$naglowek/*[local-name()='KodFormularza']"/>
		<xsl:variable name="kod2" select="$alternatywny-naglowek/*[local-name()='KodFormularza']"/>
		<xsl:variable name="wariant" select="$naglowek/*[local-name()='WariantFormularza']"/>
		<div class="naglowek">
			<table>
				<tr>
					<td colspan="2">
						<span class="kod-formularza">
							<xsl:apply-templates select="$kod"/>
						</span>
						<xsl:text> </xsl:text>
						<span class="wariant">(<xsl:apply-templates select="$wariant"/>)</span>
					</td>
				</tr>
				<tr>
					<td class="etykieta">Kod systemowy</td>
					<td class="tytulformularza">
						<xsl:value-of select="$kod/@kodSystemowy"/>
					</td>
				</tr>
				<xsl:call-template name="AtrybutNaglowka">
					<xsl:with-param name="etykieta">Kod podatku</xsl:with-param>
					<xsl:with-param name="pierwszy" select="$kod/@kodPodatku"/>
					<xsl:with-param name="drugi" select="$kod2/@kodPodatku"/>
				</xsl:call-template>
			</table>
		</div>
	</xsl:template>
	<xsl:template name="NaglowekEwidencja">
		<xsl:param name="nazwa"/>
		<xsl:param name="uzycie"/>
		<div>
			<xsl:choose>
				<xsl:when test="$uzycie = 'deklaracja'">
					<xsl:attribute name="class">tlo-formularza</xsl:attribute>
				</xsl:when>
			</xsl:choose>
			<xsl:if test="$nazwa">
				<h1 class="nazwa">
					<xsl:copy-of select="$nazwa"/>
					<br/>
				</h1>
			</xsl:if>
			<div class="okres">
				<xsl:apply-templates select="*[local-name()='Naglowek']/*[local-name()='Miesiac']"/>
				<xsl:apply-templates select="*[local-name()='Naglowek']/*[local-name()='Rok']"/>
			</div>
		</div>
	</xsl:template>
	<xsl:template name="NaglowekTytulowyEwidencja">
		<xsl:param name="nazwa"/>
		<xsl:param name="uzycie"/>
		<div>
			<xsl:choose>
				<xsl:when test="$uzycie = 'deklaracja'">
					<xsl:attribute name="class">tlo-formularza</xsl:attribute>
				</xsl:when>
			</xsl:choose>
			<xsl:if test="$nazwa">
				<h2 class="tytul-sekcja-blok">
					<span class="nazwa">
						<xsl:copy-of select="$nazwa"/>
						<br/>
					</span>
				</h2>
			</xsl:if>
		</div>
	</xsl:template>
	<xsl:template name="PouczeniaKoncowe">
		<xsl:if test="pf:Deklaracja/pf:Pouczenia ='1'">
			<h2 class="tekst">Pouczenia</h2>
			<h3 align="justify">
        W przypadku niewpłacenia w obowiązującym terminie podatku podlegającego wpłacie do urzędu skarbowego lub wpłacenia go w niepełnej wysokości niniejsza deklaracja stanowi podstawę do wystawienia tytułu wykonawczego zgodnie z przepisami o postępowaniu egzekucyjnym w administracji.<br/>
				<br/>
        Za podanie nieprawdy lub zatajenie prawdy i przez to narażenie podatku na uszczuplenie grozi odpowiedzialność przewidziana w przepisach Kodeksu karnego skarbowego.
			</h3>
			<br/>
			<br/>
		</xsl:if>
		<xsl:if test="$root = ''">
		<div class="lamstrone"/>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet>
