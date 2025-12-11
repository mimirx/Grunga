-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: grunga
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `badges`
--

DROP TABLE IF EXISTS `badges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `badges` (
  `badgeId` int NOT NULL AUTO_INCREMENT,
  `code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`badgeId`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `badges`
--

LOCK TABLES `badges` WRITE;
/*!40000 ALTER TABLE `badges` DISABLE KEYS */;
INSERT INTO `badges` VALUES (1,'BOSS_SLAYER','Boss Slayer','Defeat a weekly boss'),(2,'STREAK_7','Streak Master','Complete a 7-day streak'),(6,'FIRST_WORKOUT','First Workout Logged','Logged your first workout!'),(7,'BOSS_PYRO','Pyro Conqueror','Defeat the Pyro boss'),(8,'BOSS_NOVA','Nova Tamer','Defeat the Nova boss'),(9,'BOSS_GRUNGA','Grunga Prime','Defeat the final weekly boss'),(10,'STREAK_3','3-Week Crusher','Maintain a 3-week workout streak'),(11,'STREAK_5','5-Week Sentinel','Maintain a 5-week workout streak'),(12,'STREAK_10','10-Week Master','Maintain a 10-week workout streak'),(13,'CHALLENGE_3','Challenge Contender','Complete 3 friend challenges'),(14,'CHALLENGE_5','Challenge Rookie','Complete 5 friend challenges'),(15,'CHALLENGE_10','Challenge Veteran','Complete 10 friend challenges');
/*!40000 ALTER TABLE `badges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `challenges`
--

DROP TABLE IF EXISTS `challenges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `challenges` (
  `challengeId` int NOT NULL AUTO_INCREMENT,
  `fromUserId` int NOT NULL,
  `toUserId` int NOT NULL,
  `exerciseType` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sets` int NOT NULL,
  `reps` int NOT NULL,
  `points` int NOT NULL,
  `status` enum('PENDING','ACTIVE','COMPLETED','EXPIRED','DECLINED') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'PENDING',
  `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dueAt` datetime NOT NULL,
  PRIMARY KEY (`challengeId`),
  KEY `fromUserId` (`fromUserId`),
  KEY `toUserId` (`toUserId`),
  CONSTRAINT `challenges_ibfk_1` FOREIGN KEY (`fromUserId`) REFERENCES `users` (`userId`) ON DELETE CASCADE,
  CONSTRAINT `challenges_ibfk_2` FOREIGN KEY (`toUserId`) REFERENCES `users` (`userId`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `challenges`
--

LOCK TABLES `challenges` WRITE;
/*!40000 ALTER TABLE `challenges` DISABLE KEYS */;
INSERT INTO `challenges` VALUES (1,1,2,'pushups',1,5,5,'COMPLETED','2025-11-26 12:45:05','2025-11-26 23:59:59'),(2,2,1,'squats',1,5,5,'DECLINED','2025-11-26 13:11:05','2025-11-26 23:59:59'),(3,2,1,'squats',5,10,50,'COMPLETED','2025-11-26 13:11:57','2025-11-26 23:59:59'),(4,1,2,'pushups',1,5,5,'COMPLETED','2025-12-03 16:22:48','2025-12-03 23:59:59'),(5,2,1,'pullups',10,10,100,'COMPLETED','2025-12-05 12:38:52','2025-12-05 23:59:59'),(6,2,1,'squats',1,5,5,'COMPLETED','2025-12-05 14:28:23','2025-12-05 23:59:59'),(7,2,1,'pushups',1,5,5,'COMPLETED','2025-12-09 17:09:42','2025-12-09 23:59:59'),(8,2,1,'squats',1,5,5,'COMPLETED','2025-12-11 13:12:39','2025-12-11 23:59:59');
/*!40000 ALTER TABLE `challenges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dailypoints`
--

DROP TABLE IF EXISTS `dailypoints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dailypoints` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `day` date NOT NULL,
  `points` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_day` (`userId`,`day`),
  CONSTRAINT `dailypoints_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `users` (`userId`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dailypoints`
--

LOCK TABLES `dailypoints` WRITE;
/*!40000 ALTER TABLE `dailypoints` DISABLE KEYS */;
INSERT INTO `dailypoints` VALUES (1,1,'2025-11-19',40),(2,2,'2025-11-19',110),(3,1,'2025-11-20',0),(4,2,'2025-11-20',120);
/*!40000 ALTER TABLE `dailypoints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `friends`
--

DROP TABLE IF EXISTS `friends`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `friends` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `friendId` int NOT NULL,
  `initiatedBy` int DEFAULT NULL,
  `status` enum('pending','accepted','blocked') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `createdAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uc_friend_pair` (`userId`,`friendId`),
  KEY `fk_friends_initiatedBy` (`initiatedBy`),
  CONSTRAINT `fk_friends_initiatedBy` FOREIGN KEY (`initiatedBy`) REFERENCES `users` (`userId`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `friends`
--

LOCK TABLES `friends` WRITE;
/*!40000 ALTER TABLE `friends` DISABLE KEYS */;
INSERT INTO `friends` VALUES (19,1,2,1,'accepted','2025-12-11 19:07:36','2025-12-11 19:07:59');
/*!40000 ALTER TABLE `friends` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pointsledger`
--

DROP TABLE IF EXISTS `pointsledger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pointsledger` (
  `ledgerId` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `points` int NOT NULL,
  `reason` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `refId` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `occurredAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ledgerId`),
  KEY `idx_ledger_user_time` (`userId`,`occurredAt`),
  CONSTRAINT `fk_ledger_user` FOREIGN KEY (`userId`) REFERENCES `users` (`userId`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pointsledger`
--

LOCK TABLES `pointsledger` WRITE;
/*!40000 ALTER TABLE `pointsledger` DISABLE KEYS */;
/*!40000 ALTER TABLE `pointsledger` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pointstotals`
--

DROP TABLE IF EXISTS `pointstotals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pointstotals` (
  `userId` int NOT NULL,
  `dailyPoints` int NOT NULL DEFAULT '0',
  `weeklyPoints` int NOT NULL DEFAULT '0',
  `totalPoints` int NOT NULL DEFAULT '0',
  `updatedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `streak` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`userId`),
  CONSTRAINT `fk_totals_user` FOREIGN KEY (`userId`) REFERENCES `users` (`userId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pointstotals`
--

LOCK TABLES `pointstotals` WRITE;
/*!40000 ALTER TABLE `pointstotals` DISABLE KEYS */;
/*!40000 ALTER TABLE `pointstotals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userbadges`
--

DROP TABLE IF EXISTS `userbadges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userbadges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `badgeId` int NOT NULL,
  `unlockedAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_badge` (`userId`,`badgeId`),
  KEY `fk_ub_badge` (`badgeId`),
  CONSTRAINT `fk_ub_badge` FOREIGN KEY (`badgeId`) REFERENCES `badges` (`badgeId`) ON DELETE CASCADE,
  CONSTRAINT `fk_ub_user` FOREIGN KEY (`userId`) REFERENCES `users` (`userId`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userbadges`
--

LOCK TABLES `userbadges` WRITE;
/*!40000 ALTER TABLE `userbadges` DISABLE KEYS */;
INSERT INTO `userbadges` VALUES (1,1,6,'2025-12-01 15:13:48'),(2,2,1,'2025-12-01 15:28:07'),(3,1,1,'2025-12-17 18:12:40');
/*!40000 ALTER TABLE `userbadges` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `userId` int NOT NULL AUTO_INCREMENT,
  `username` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `displayName` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'User',
  `email` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createdAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`userId`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'demo1','Demo One',NULL,'2025-11-07 12:52:09'),(2,'demo2','Demo Two',NULL,'2025-11-07 12:52:09');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workouts`
--

DROP TABLE IF EXISTS `workouts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workouts` (
  `workoutId` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `workoutDate` date NOT NULL,
  `workoutType` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sets` int NOT NULL,
  `reps` int NOT NULL,
  `createdAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`workoutId`),
  KEY `idx_workouts_user_date` (`userId`,`workoutDate`),
  CONSTRAINT `fk_workouts_user` FOREIGN KEY (`userId`) REFERENCES `users` (`userId`) ON DELETE CASCADE,
  CONSTRAINT `workouts_chk_1` CHECK ((`sets` > 0)),
  CONSTRAINT `workouts_chk_2` CHECK ((`reps` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workouts`
--

LOCK TABLES `workouts` WRITE;
/*!40000 ALTER TABLE `workouts` DISABLE KEYS */;
/*!40000 ALTER TABLE `workouts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-11 14:01:12
