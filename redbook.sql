CREATE DATABASE IF NOT EXISTS `redbook` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for config
-- ----------------------------
DROP TABLE IF EXISTS `config`;
CREATE TABLE `config`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `isMultiKey` tinyint(1) NULL DEFAULT 0,
  `searchKey` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `selectedFilter` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '最新',
  `selectedCategory` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '先图文后视频',
  `taskCount` int(11) NULL DEFAULT 200,
  `isCyclicMode` tinyint(1) NULL DEFAULT 1,
  `waitTime` int(11) NULL DEFAULT 5,
  `isToLike` tinyint(1) NULL DEFAULT 0,
  `isToCollect` tinyint(1) NULL DEFAULT 1,
  `isToFollow` tinyint(1) NULL DEFAULT 0,
  `isComment` tinyint(1) NULL DEFAULT 1,
  `commentMode` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '跳过已收藏',
  `isRandomRareWords` tinyint(1) NULL DEFAULT 0,
  `rareWordsCount` int(11) NULL DEFAULT 3,
  `isCheckFailure` tinyint(1) NULL DEFAULT 1,
  `isRetryAfterFailure` tinyint(1) NULL DEFAULT 0,
  `retryTimes` int(11) NULL DEFAULT 3,
  `isRandomIntervalTime` tinyint(1) NULL DEFAULT 1,
  `intervalTime` int(11) NULL DEFAULT 5,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for spiders
-- ----------------------------
DROP TABLE IF EXISTS `spiders`;
CREATE TABLE `spiders`  (
  `sid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `state` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `createTime` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `isMultiKey` tinyint(1) NULL DEFAULT NULL,
  `searchKey` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `selectedFilter` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `selectedCategory` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `taskCount` int(11) NULL DEFAULT NULL,
  `isCyclicMode` tinyint(1) NULL DEFAULT NULL,
  `waitTime` int(11) NULL DEFAULT NULL,
  `isToLike` tinyint(1) NULL DEFAULT NULL,
  `isToCollect` tinyint(1) NULL DEFAULT NULL,
  `isToFollow` tinyint(1) NULL DEFAULT NULL,
  `isComment` tinyint(1) NULL DEFAULT NULL,
  `commentMode` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `isRandomRareWords` tinyint(1) NULL DEFAULT NULL,
  `rareWordsCount` int(11) NULL DEFAULT NULL,
  `isCheckFailure` tinyint(1) NULL DEFAULT NULL,
  `isRetryAfterFailure` tinyint(1) NULL DEFAULT NULL,
  `retryTimes` int(11) NULL DEFAULT NULL,
  `isRandomIntervalTime` tinyint(1) NULL DEFAULT NULL,
  `intervalTime` int(11) NULL DEFAULT NULL,
  `run` tinyint(1) NULL DEFAULT NULL,
  `showQrCode` tinyint(1) NULL DEFAULT NULL,
  `showQrCodeState` tinyint(1) NULL DEFAULT NULL,
  `qrCodeState` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `secureSession` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `session` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `userId` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  PRIMARY KEY (`sid`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
