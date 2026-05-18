-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: May 16, 2026 at 04:18 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `F1Fitora`
--

-- --------------------------------------------------------

--
-- Table structure for table `adminpanel_admincustomer`
--

CREATE TABLE `adminpanel_admincustomer` (
  `id` bigint(20) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `address` longtext DEFAULT NULL,
  `profile_pic` varchar(100) DEFAULT NULL,
  `total_spent` decimal(10,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `adminpanel_adminorder`
--

CREATE TABLE `adminpanel_adminorder` (
  `id` bigint(20) NOT NULL,
  `order_number` varchar(50) NOT NULL,
  `description` longtext NOT NULL,
  `measurements` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`measurements`)),
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `priority` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `delivery_date` date DEFAULT NULL,
  `cancellation_reason` longtext DEFAULT NULL,
  `refund_issued` tinyint(1) NOT NULL,
  `rating` int(11) NOT NULL,
  `customer_id` bigint(20) NOT NULL,
  `tailor_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `adminpanel_adminpayment`
--

CREATE TABLE `adminpanel_adminpayment` (
  `id` bigint(20) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_method` varchar(20) NOT NULL,
  `transaction_ref` varchar(100) NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `customer_id` bigint(20) NOT NULL,
  `order_id` bigint(20) NOT NULL,
  `tailor_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `adminpanel_adminprofile`
--

CREATE TABLE `adminpanel_adminprofile` (
  `id` bigint(20) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `profile_pic` varchar(100) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `adminpanel_admintailor`
--

CREATE TABLE `adminpanel_admintailor` (
  `id` bigint(20) NOT NULL,
  `name` varchar(200) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `specialty` varchar(50) NOT NULL,
  `profile_pic` varchar(100) DEFAULT NULL,
  `address` longtext DEFAULT NULL,
  `experience_years` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `completed_orders` int(11) NOT NULL,
  `total_earnings` decimal(10,2) NOT NULL,
  `avg_rating` decimal(3,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `adminpanel_admintransactionrecord`
--

CREATE TABLE `adminpanel_admintransactionrecord` (
  `id` bigint(20) NOT NULL,
  `gateway_id` varchar(100) NOT NULL,
  `gateway_fee` decimal(10,2) NOT NULL,
  `net_amount` decimal(10,2) NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `processed_date` datetime(6) NOT NULL,
  `response_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`response_data`)),
  `payment_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add admin profile', 1, 'add_adminprofile'),
(2, 'Can change admin profile', 1, 'change_adminprofile'),
(3, 'Can delete admin profile', 1, 'delete_adminprofile'),
(4, 'Can view admin profile', 1, 'view_adminprofile'),
(5, 'Can add admin customer', 2, 'add_admincustomer'),
(6, 'Can change admin customer', 2, 'change_admincustomer'),
(7, 'Can delete admin customer', 2, 'delete_admincustomer'),
(8, 'Can view admin customer', 2, 'view_admincustomer'),
(9, 'Can add admin order', 3, 'add_adminorder'),
(10, 'Can change admin order', 3, 'change_adminorder'),
(11, 'Can delete admin order', 3, 'delete_adminorder'),
(12, 'Can view admin order', 3, 'view_adminorder'),
(13, 'Can add admin payment', 4, 'add_adminpayment'),
(14, 'Can change admin payment', 4, 'change_adminpayment'),
(15, 'Can delete admin payment', 4, 'delete_adminpayment'),
(16, 'Can view admin payment', 4, 'view_adminpayment'),
(17, 'Can add admin tailor', 5, 'add_admintailor'),
(18, 'Can change admin tailor', 5, 'change_admintailor'),
(19, 'Can delete admin tailor', 5, 'delete_admintailor'),
(20, 'Can view admin tailor', 5, 'view_admintailor'),
(21, 'Can add admin transaction record', 6, 'add_admintransactionrecord'),
(22, 'Can change admin transaction record', 6, 'change_admintransactionrecord'),
(23, 'Can delete admin transaction record', 6, 'delete_admintransactionrecord'),
(24, 'Can view admin transaction record', 6, 'view_admintransactionrecord'),
(25, 'Can add tailor', 7, 'add_tailor'),
(26, 'Can change tailor', 7, 'change_tailor'),
(27, 'Can delete tailor', 7, 'delete_tailor'),
(28, 'Can view tailor', 7, 'view_tailor'),
(29, 'Can add tailor customer', 8, 'add_tailorcustomer'),
(30, 'Can change tailor customer', 8, 'change_tailorcustomer'),
(31, 'Can delete tailor customer', 8, 'delete_tailorcustomer'),
(32, 'Can view tailor customer', 8, 'view_tailorcustomer'),
(33, 'Can add tailor order', 9, 'add_tailororder'),
(34, 'Can change tailor order', 9, 'change_tailororder'),
(35, 'Can delete tailor order', 9, 'delete_tailororder'),
(36, 'Can view tailor order', 9, 'view_tailororder'),
(37, 'Can add tailor payment', 10, 'add_tailorpayment'),
(38, 'Can change tailor payment', 10, 'change_tailorpayment'),
(39, 'Can delete tailor payment', 10, 'delete_tailorpayment'),
(40, 'Can view tailor payment', 10, 'view_tailorpayment'),
(41, 'Can add tailor measurement', 11, 'add_tailormeasurement'),
(42, 'Can change tailor measurement', 11, 'change_tailormeasurement'),
(43, 'Can delete tailor measurement', 11, 'delete_tailormeasurement'),
(44, 'Can view tailor measurement', 11, 'view_tailormeasurement'),
(45, 'Can add log entry', 12, 'add_logentry'),
(46, 'Can change log entry', 12, 'change_logentry'),
(47, 'Can delete log entry', 12, 'delete_logentry'),
(48, 'Can view log entry', 12, 'view_logentry'),
(49, 'Can add permission', 13, 'add_permission'),
(50, 'Can change permission', 13, 'change_permission'),
(51, 'Can delete permission', 13, 'delete_permission'),
(52, 'Can view permission', 13, 'view_permission'),
(53, 'Can add group', 14, 'add_group'),
(54, 'Can change group', 14, 'change_group'),
(55, 'Can delete group', 14, 'delete_group'),
(56, 'Can view group', 14, 'view_group'),
(57, 'Can add user', 15, 'add_user'),
(58, 'Can change user', 15, 'change_user'),
(59, 'Can delete user', 15, 'delete_user'),
(60, 'Can view user', 15, 'view_user'),
(61, 'Can add content type', 16, 'add_contenttype'),
(62, 'Can change content type', 16, 'change_contenttype'),
(63, 'Can delete content type', 16, 'delete_contenttype'),
(64, 'Can view content type', 16, 'view_contenttype'),
(65, 'Can add session', 17, 'add_session'),
(66, 'Can change session', 17, 'change_session'),
(67, 'Can delete session', 17, 'delete_session'),
(68, 'Can view session', 17, 'view_session'),
(69, 'Can add customer order', 18, 'add_customerorder'),
(70, 'Can change customer order', 18, 'change_customerorder'),
(71, 'Can delete customer order', 18, 'delete_customerorder'),
(72, 'Can view customer order', 18, 'view_customerorder'),
(73, 'Can add customer payment', 19, 'add_customerpayment'),
(74, 'Can change customer payment', 19, 'change_customerpayment'),
(75, 'Can delete customer payment', 19, 'delete_customerpayment'),
(76, 'Can view customer payment', 19, 'view_customerpayment'),
(77, 'Can add customer address', 20, 'add_customeraddress'),
(78, 'Can change customer address', 20, 'change_customeraddress'),
(79, 'Can delete customer address', 20, 'delete_customeraddress'),
(80, 'Can view customer address', 20, 'view_customeraddress'),
(81, 'Can add customer', 21, 'add_customer'),
(82, 'Can change customer', 21, 'change_customer'),
(83, 'Can delete customer', 21, 'delete_customer'),
(84, 'Can view customer', 21, 'view_customer');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customer_customer`
--

CREATE TABLE `customer_customer` (
  `id` bigint(20) NOT NULL,
  `username` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `mobile` varchar(15) NOT NULL,
  `password` varchar(255) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `profile_pic` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer_customer`
--

INSERT INTO `customer_customer` (`id`, `username`, `email`, `mobile`, `password`, `first_name`, `last_name`, `profile_pic`, `is_active`, `is_verified`, `created_at`, `updated_at`) VALUES
(1, 'sky', 'skyraval1911@gmail.com', '6356828909', 'pbkdf2_sha256$600000$DjCuFCWBTj69nKSPf7vznW$yPuB8NCvnykDXlyYkFdHbLuvNOSDNaAvc85KQ/MfsfQ=', NULL, NULL, '', 1, 0, '2026-05-16 13:37:15.775148', '2026-05-16 13:37:15.775183');

-- --------------------------------------------------------

--
-- Table structure for table `customer_customeraddress`
--

CREATE TABLE `customer_customeraddress` (
  `id` bigint(20) NOT NULL,
  `full_name` varchar(200) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `street` longtext NOT NULL,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `pincode` varchar(10) NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `customer_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customer_customerorder`
--

CREATE TABLE `customer_customerorder` (
  `id` bigint(20) NOT NULL,
  `tailor_id` int(11) DEFAULT NULL,
  `tailor_name` varchar(200) DEFAULT NULL,
  `order_number` varchar(50) NOT NULL,
  `garment_type` varchar(100) NOT NULL,
  `description` longtext DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `advance_paid` decimal(10,2) NOT NULL,
  `balance_due` decimal(10,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `payment_status` varchar(20) NOT NULL,
  `delivery_date` date DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `measurements` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`measurements`)),
  `notes` longtext DEFAULT NULL,
  `customer_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `customer_customerpayment`
--

CREATE TABLE `customer_customerpayment` (
  `id` bigint(20) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_method` varchar(20) NOT NULL,
  `transaction_id` varchar(100) NOT NULL,
  `status` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `customer_id` bigint(20) NOT NULL,
  `order_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(12, 'admin', 'logentry'),
(2, 'adminpanel', 'admincustomer'),
(3, 'adminpanel', 'adminorder'),
(4, 'adminpanel', 'adminpayment'),
(1, 'adminpanel', 'adminprofile'),
(5, 'adminpanel', 'admintailor'),
(6, 'adminpanel', 'admintransactionrecord'),
(14, 'auth', 'group'),
(13, 'auth', 'permission'),
(15, 'auth', 'user'),
(16, 'contenttypes', 'contenttype'),
(21, 'customer', 'customer'),
(20, 'customer', 'customeraddress'),
(18, 'customer', 'customerorder'),
(19, 'customer', 'customerpayment'),
(17, 'sessions', 'session'),
(7, 'tailor', 'tailor'),
(8, 'tailor', 'tailorcustomer'),
(11, 'tailor', 'tailormeasurement'),
(9, 'tailor', 'tailororder'),
(10, 'tailor', 'tailorpayment');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-05-16 13:04:08.191016'),
(2, 'auth', '0001_initial', '2026-05-16 13:04:08.606926'),
(3, 'admin', '0001_initial', '2026-05-16 13:04:08.680466'),
(4, 'admin', '0002_logentry_remove_auto_add', '2026-05-16 13:04:08.688728'),
(5, 'admin', '0003_logentry_add_action_flag_choices', '2026-05-16 13:04:08.697452'),
(6, 'adminpanel', '0001_initial', '2026-05-16 13:04:09.068624'),
(7, 'adminpanel', '0002_admincustomer_adminorder_adminpayment_admintailor_and_more', '2026-05-16 13:04:09.777351'),
(8, 'contenttypes', '0002_remove_content_type_name', '2026-05-16 13:04:09.823168'),
(9, 'auth', '0002_alter_permission_name_max_length', '2026-05-16 13:04:09.864005'),
(10, 'auth', '0003_alter_user_email_max_length', '2026-05-16 13:04:09.879359'),
(11, 'auth', '0004_alter_user_username_opts', '2026-05-16 13:04:09.889442'),
(12, 'auth', '0005_alter_user_last_login_null', '2026-05-16 13:04:09.924019'),
(13, 'auth', '0006_require_contenttypes_0002', '2026-05-16 13:04:09.926839'),
(14, 'auth', '0007_alter_validators_add_error_messages', '2026-05-16 13:04:09.938692'),
(15, 'auth', '0008_alter_user_username_max_length', '2026-05-16 13:04:09.956495'),
(16, 'auth', '0009_alter_user_last_name_max_length', '2026-05-16 13:04:09.973492'),
(17, 'auth', '0010_alter_group_name_max_length', '2026-05-16 13:04:09.994937'),
(18, 'auth', '0011_update_proxy_permissions', '2026-05-16 13:04:10.008891'),
(19, 'auth', '0012_alter_user_first_name_max_length', '2026-05-16 13:04:10.062494'),
(20, 'sessions', '0001_initial', '2026-05-16 13:04:10.091650'),
(21, 'tailor', '0001_initial', '2026-05-16 13:04:10.531597'),
(22, 'customer', '0001_initial', '2026-05-16 13:24:49.198145');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tailor_tailor`
--

CREATE TABLE `tailor_tailor` (
  `id` bigint(20) NOT NULL,
  `username` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `mobile` varchar(15) NOT NULL,
  `password` varchar(255) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `profile_pic` varchar(100) DEFAULT NULL,
  `specialty` varchar(50) NOT NULL,
  `years_of_experience` int(11) NOT NULL,
  `bio` longtext DEFAULT NULL,
  `shop_name` varchar(200) DEFAULT NULL,
  `shop_address` longtext DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `opening_time` time(6) DEFAULT NULL,
  `closing_time` time(6) DEFAULT NULL,
  `working_days` varchar(100) NOT NULL,
  `is_open` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `total_earnings` decimal(12,2) NOT NULL,
  `pending_balance` decimal(12,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tailor_tailor`
--

INSERT INTO `tailor_tailor` (`id`, `username`, `email`, `mobile`, `password`, `first_name`, `last_name`, `profile_pic`, `specialty`, `years_of_experience`, `bio`, `shop_name`, `shop_address`, `city`, `opening_time`, `closing_time`, `working_days`, `is_open`, `is_active`, `is_verified`, `created_at`, `updated_at`, `total_earnings`, `pending_balance`) VALUES
(1, 'Jinal', 'jinal@gmail.com', '6356828909', 'pbkdf2_sha256$600000$frcWVGyWOhgNikS9u7LtvI$Yc75dTwSWsMs11kMLaiQx2rfypcrbRNDRLzi/ARCG+Y=', NULL, NULL, '', 'Suits & Blazers', 0, NULL, NULL, NULL, NULL, NULL, NULL, 'Mon-Sat', 1, 1, 0, '2026-05-16 13:06:04.609366', '2026-05-16 13:06:04.609399', 0.00, 0.00),
(2, 'akash', 'skyraval1911@gmail.com', '9099182609', 'pbkdf2_sha256$600000$3mwW4538Xb581mdiDx9riY$uYAotZgBJNPfkOOFvhswhMtmMx4e3i9EqgzAldC3S2o=', NULL, NULL, '', 'Suits & Blazers', 0, NULL, NULL, NULL, NULL, NULL, NULL, 'Mon-Sat', 1, 1, 0, '2026-05-16 13:10:34.951735', '2026-05-16 13:10:34.951768', 0.00, 0.00);

-- --------------------------------------------------------

--
-- Table structure for table `tailor_tailorcustomer`
--

CREATE TABLE `tailor_tailorcustomer` (
  `id` bigint(20) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `phone_number` varchar(15) NOT NULL,
  `address` longtext DEFAULT NULL,
  `customer_measurements` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`customer_measurements`)),
  `notes` longtext DEFAULT NULL,
  `profile_pic` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `tailor_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tailor_tailormeasurement`
--

CREATE TABLE `tailor_tailormeasurement` (
  `id` bigint(20) NOT NULL,
  `neck` decimal(5,1) DEFAULT NULL,
  `chest` decimal(5,1) DEFAULT NULL,
  `waist` decimal(5,1) DEFAULT NULL,
  `hip` decimal(5,1) DEFAULT NULL,
  `shoulder` decimal(5,1) DEFAULT NULL,
  `sleeve_length` decimal(5,1) DEFAULT NULL,
  `inseam` decimal(5,1) DEFAULT NULL,
  `length` decimal(5,1) DEFAULT NULL,
  `bicep` decimal(5,1) DEFAULT NULL,
  `thigh` decimal(5,1) DEFAULT NULL,
  `calf` decimal(5,1) DEFAULT NULL,
  `notes` longtext DEFAULT NULL,
  `measurement_date` date NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `customer_id` bigint(20) NOT NULL,
  `tailor_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tailor_tailororder`
--

CREATE TABLE `tailor_tailororder` (
  `id` bigint(20) NOT NULL,
  `order_number` varchar(50) NOT NULL,
  `garment_type` varchar(100) NOT NULL,
  `description` longtext DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `advance_paid` decimal(10,2) NOT NULL,
  `balance_due` decimal(10,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `priority` varchar(10) NOT NULL,
  `delivery_date` date NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `cancellation_reason` longtext DEFAULT NULL,
  `is_refunded` tinyint(1) NOT NULL,
  `customer_id` bigint(20) NOT NULL,
  `tailor_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tailor_tailorpayment`
--

CREATE TABLE `tailor_tailorpayment` (
  `id` bigint(20) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `method` varchar(20) NOT NULL,
  `status` varchar(10) NOT NULL,
  `note` longtext DEFAULT NULL,
  `receipt_number` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `customer_id` bigint(20) NOT NULL,
  `order_id` bigint(20) NOT NULL,
  `tailor_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `adminpanel_admincustomer`
--
ALTER TABLE `adminpanel_admincustomer`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `adminpanel_adminorder`
--
ALTER TABLE `adminpanel_adminorder`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `adminpanel_adminorde_tailor_id_ce7475e8_fk_adminpane` (`tailor_id`),
  ADD KEY `adminpanel_adminorde_customer_id_228f2642_fk_adminpane` (`customer_id`);

--
-- Indexes for table `adminpanel_adminpayment`
--
ALTER TABLE `adminpanel_adminpayment`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `transaction_ref` (`transaction_ref`),
  ADD KEY `adminpanel_adminpaym_tailor_id_bd989d8f_fk_adminpane` (`tailor_id`),
  ADD KEY `adminpanel_adminpaym_customer_id_f2ee0e12_fk_adminpane` (`customer_id`),
  ADD KEY `adminpanel_adminpaym_order_id_30b2aa15_fk_adminpane` (`order_id`);

--
-- Indexes for table `adminpanel_adminprofile`
--
ALTER TABLE `adminpanel_adminprofile`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `adminpanel_admintailor`
--
ALTER TABLE `adminpanel_admintailor`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `adminpanel_admintransactionrecord`
--
ALTER TABLE `adminpanel_admintransactionrecord`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `payment_id` (`payment_id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `customer_customer`
--
ALTER TABLE `customer_customer`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `customer_customeraddress`
--
ALTER TABLE `customer_customeraddress`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_customeradd_customer_id_7e9862e1_fk_customer_` (`customer_id`);

--
-- Indexes for table `customer_customerorder`
--
ALTER TABLE `customer_customerorder`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `customer_customerord_customer_id_2d8f3e11_fk_customer_` (`customer_id`);

--
-- Indexes for table `customer_customerpayment`
--
ALTER TABLE `customer_customerpayment`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `transaction_id` (`transaction_id`),
  ADD KEY `customer_customerpay_customer_id_e7a591d9_fk_customer_` (`customer_id`),
  ADD KEY `customer_customerpay_order_id_bd447ee5_fk_customer_` (`order_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `tailor_tailor`
--
ALTER TABLE `tailor_tailor`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `tailor_tailorcustomer`
--
ALTER TABLE `tailor_tailorcustomer`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tailor_tailorcustomer_tailor_id_4f0834b5_fk_tailor_tailor_id` (`tailor_id`);

--
-- Indexes for table `tailor_tailormeasurement`
--
ALTER TABLE `tailor_tailormeasurement`
  ADD PRIMARY KEY (`id`),
  ADD KEY `tailor_tailormeasure_customer_id_e34dcc22_fk_tailor_ta` (`customer_id`),
  ADD KEY `tailor_tailormeasurement_tailor_id_11939074_fk_tailor_tailor_id` (`tailor_id`);

--
-- Indexes for table `tailor_tailororder`
--
ALTER TABLE `tailor_tailororder`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `tailor_tailororder_customer_id_2bc4cefb_fk_tailor_ta` (`customer_id`),
  ADD KEY `tailor_tailororder_tailor_id_44260c66_fk_tailor_tailor_id` (`tailor_id`);

--
-- Indexes for table `tailor_tailorpayment`
--
ALTER TABLE `tailor_tailorpayment`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `receipt_number` (`receipt_number`),
  ADD KEY `tailor_tailorpayment_customer_id_e360a22a_fk_tailor_ta` (`customer_id`),
  ADD KEY `tailor_tailorpayment_order_id_158f37e1_fk_tailor_tailororder_id` (`order_id`),
  ADD KEY `tailor_tailorpayment_tailor_id_46863b09_fk_tailor_tailor_id` (`tailor_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `adminpanel_admincustomer`
--
ALTER TABLE `adminpanel_admincustomer`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `adminpanel_adminorder`
--
ALTER TABLE `adminpanel_adminorder`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `adminpanel_adminpayment`
--
ALTER TABLE `adminpanel_adminpayment`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `adminpanel_adminprofile`
--
ALTER TABLE `adminpanel_adminprofile`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `adminpanel_admintailor`
--
ALTER TABLE `adminpanel_admintailor`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `adminpanel_admintransactionrecord`
--
ALTER TABLE `adminpanel_admintransactionrecord`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=85;

--
-- AUTO_INCREMENT for table `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customer_customer`
--
ALTER TABLE `customer_customer`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `customer_customeraddress`
--
ALTER TABLE `customer_customeraddress`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customer_customerorder`
--
ALTER TABLE `customer_customerorder`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customer_customerpayment`
--
ALTER TABLE `customer_customerpayment`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `tailor_tailor`
--
ALTER TABLE `tailor_tailor`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `tailor_tailorcustomer`
--
ALTER TABLE `tailor_tailorcustomer`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tailor_tailormeasurement`
--
ALTER TABLE `tailor_tailormeasurement`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tailor_tailororder`
--
ALTER TABLE `tailor_tailororder`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tailor_tailorpayment`
--
ALTER TABLE `tailor_tailorpayment`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `adminpanel_admincustomer`
--
ALTER TABLE `adminpanel_admincustomer`
  ADD CONSTRAINT `adminpanel_admincustomer_user_id_f6013f3e_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `adminpanel_adminorder`
--
ALTER TABLE `adminpanel_adminorder`
  ADD CONSTRAINT `adminpanel_adminorde_customer_id_228f2642_fk_adminpane` FOREIGN KEY (`customer_id`) REFERENCES `adminpanel_admincustomer` (`id`),
  ADD CONSTRAINT `adminpanel_adminorde_tailor_id_ce7475e8_fk_adminpane` FOREIGN KEY (`tailor_id`) REFERENCES `adminpanel_admintailor` (`id`);

--
-- Constraints for table `adminpanel_adminpayment`
--
ALTER TABLE `adminpanel_adminpayment`
  ADD CONSTRAINT `adminpanel_adminpaym_customer_id_f2ee0e12_fk_adminpane` FOREIGN KEY (`customer_id`) REFERENCES `adminpanel_admincustomer` (`id`),
  ADD CONSTRAINT `adminpanel_adminpaym_order_id_30b2aa15_fk_adminpane` FOREIGN KEY (`order_id`) REFERENCES `adminpanel_adminorder` (`id`),
  ADD CONSTRAINT `adminpanel_adminpaym_tailor_id_bd989d8f_fk_adminpane` FOREIGN KEY (`tailor_id`) REFERENCES `adminpanel_admintailor` (`id`);

--
-- Constraints for table `adminpanel_adminprofile`
--
ALTER TABLE `adminpanel_adminprofile`
  ADD CONSTRAINT `adminpanel_adminprofile_user_id_42449e64_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `adminpanel_admintransactionrecord`
--
ALTER TABLE `adminpanel_admintransactionrecord`
  ADD CONSTRAINT `adminpanel_admintran_payment_id_2f2b622d_fk_adminpane` FOREIGN KEY (`payment_id`) REFERENCES `adminpanel_adminpayment` (`id`);

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `customer_customeraddress`
--
ALTER TABLE `customer_customeraddress`
  ADD CONSTRAINT `customer_customeradd_customer_id_7e9862e1_fk_customer_` FOREIGN KEY (`customer_id`) REFERENCES `customer_customer` (`id`);

--
-- Constraints for table `customer_customerorder`
--
ALTER TABLE `customer_customerorder`
  ADD CONSTRAINT `customer_customerord_customer_id_2d8f3e11_fk_customer_` FOREIGN KEY (`customer_id`) REFERENCES `customer_customer` (`id`);

--
-- Constraints for table `customer_customerpayment`
--
ALTER TABLE `customer_customerpayment`
  ADD CONSTRAINT `customer_customerpay_customer_id_e7a591d9_fk_customer_` FOREIGN KEY (`customer_id`) REFERENCES `customer_customer` (`id`),
  ADD CONSTRAINT `customer_customerpay_order_id_bd447ee5_fk_customer_` FOREIGN KEY (`order_id`) REFERENCES `customer_customerorder` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `tailor_tailorcustomer`
--
ALTER TABLE `tailor_tailorcustomer`
  ADD CONSTRAINT `tailor_tailorcustomer_tailor_id_4f0834b5_fk_tailor_tailor_id` FOREIGN KEY (`tailor_id`) REFERENCES `tailor_tailor` (`id`);

--
-- Constraints for table `tailor_tailormeasurement`
--
ALTER TABLE `tailor_tailormeasurement`
  ADD CONSTRAINT `tailor_tailormeasure_customer_id_e34dcc22_fk_tailor_ta` FOREIGN KEY (`customer_id`) REFERENCES `tailor_tailorcustomer` (`id`),
  ADD CONSTRAINT `tailor_tailormeasurement_tailor_id_11939074_fk_tailor_tailor_id` FOREIGN KEY (`tailor_id`) REFERENCES `tailor_tailor` (`id`);

--
-- Constraints for table `tailor_tailororder`
--
ALTER TABLE `tailor_tailororder`
  ADD CONSTRAINT `tailor_tailororder_customer_id_2bc4cefb_fk_tailor_ta` FOREIGN KEY (`customer_id`) REFERENCES `tailor_tailorcustomer` (`id`),
  ADD CONSTRAINT `tailor_tailororder_tailor_id_44260c66_fk_tailor_tailor_id` FOREIGN KEY (`tailor_id`) REFERENCES `tailor_tailor` (`id`);

--
-- Constraints for table `tailor_tailorpayment`
--
ALTER TABLE `tailor_tailorpayment`
  ADD CONSTRAINT `tailor_tailorpayment_customer_id_e360a22a_fk_tailor_ta` FOREIGN KEY (`customer_id`) REFERENCES `tailor_tailorcustomer` (`id`),
  ADD CONSTRAINT `tailor_tailorpayment_order_id_158f37e1_fk_tailor_tailororder_id` FOREIGN KEY (`order_id`) REFERENCES `tailor_tailororder` (`id`),
  ADD CONSTRAINT `tailor_tailorpayment_tailor_id_46863b09_fk_tailor_tailor_id` FOREIGN KEY (`tailor_id`) REFERENCES `tailor_tailor` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
