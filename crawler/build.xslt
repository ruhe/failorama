<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="/freeStyleProject">
        <root>
            <builds>
                <xsl:for-each select="build">
                    <build>
                        <number>
                            <xsl:value-of select="number"/>
                        </number>
                        <result>
                            <xsl:value-of select="result"/>
                        </result>
                        <timestamp>
                            <xsl:value-of select="timestamp"/>
                        </timestamp>
                        <description>
                            <xsl:value-of select="description"/>
                        </description>
                        <upstreamBuild>
                            <xsl:value-of select="action/cause/upstreamBuild"/>
                        </upstreamBuild>
                        <upstreamProject>
                            <xsl:value-of select="action/cause/upstreamProject"/>
                        </upstreamProject>
                    </build>
                </xsl:for-each>
            </builds>
            <downsteam>
                <xsl:for-each select="downstreamProject">
                    <job>
                        <name>
                            <xsl:value-of select="name"/>
                        </name>
                        <builds>
                            <xsl:for-each select="build">
                                <build>
                                    <number>
                                        <xsl:value-of select="number"/>
                                    </number>
                                </build>
                            </xsl:for-each>
                        </builds>
                    </job>
                </xsl:for-each>
            </downsteam>
        </root>
    </xsl:template>


</xsl:stylesheet>