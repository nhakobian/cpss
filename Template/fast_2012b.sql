--
-- Database: `carmaproposals`
--

-- --------------------------------------------------------

--
-- Table structure for table `fast_source`
--

CREATE TABLE IF NOT EXISTS `fast_source` (
  `proposalid` bigint(20) NOT NULL DEFAULT '0',
  `numb` bigint(20) NOT NULL DEFAULT '1',
  `f_sourcename` text COLLATE utf8_unicode_ci,
  `f_ra` text COLLATE utf8_unicode_ci,
  `f_dec` text COLLATE utf8_unicode_ci,
  `f_vlsr` text COLLATE utf8_unicode_ci,
  `f_time` text COLLATE utf8_unicode_ci,
  `f_corrconfig` text COLLATE utf8_unicode_ci,
  `f_freq` text COLLATE utf8_unicode_ci,
  `f_slbw` text COLLATE utf8_unicode_ci,
  `f_mosaic` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`proposalid`,`numb`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

