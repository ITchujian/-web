/*
 Navicat Premium Data Transfer

 Source Server         : Flask1
 Source Server Type    : MySQL
 Source Server Version : 50743 (5.7.43)
 Source Host           : localhost:3306
 Source Schema         : redbook

 Target Server Type    : MySQL
 Target Server Version : 50743 (5.7.43)
 File Encoding         : 65001

 Date: 04/11/2023 22:04:35
*/

CREATE DATABASE IF NOT EXISTS `redbook` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE `redbook`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for config
-- ----------------------------
DROP TABLE IF EXISTS `config`;
CREATE TABLE `config`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `isMultiKey` tinyint(1) NULL DEFAULT 0,
  `searchKey` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `selectedFilter` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '最新',
  `selectedCategory` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '先图文后视频',
  `taskCount` int(11) NULL DEFAULT 200,
  `isCyclicMode` tinyint(1) NULL DEFAULT 1,
  `waitTime` int(11) NULL DEFAULT 5,
  `isToLike` tinyint(1) NULL DEFAULT 0,
  `isToCollect` tinyint(1) NULL DEFAULT 1,
  `isToFollow` tinyint(1) NULL DEFAULT 0,
  `isComment` tinyint(1) NULL DEFAULT 1,
  `commentMode` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '跳过已收藏',
  `isRandomRareWords` tinyint(1) NULL DEFAULT 0,
  `rareWordsCount` int(11) NULL DEFAULT 3,
  `isCheckFailure` tinyint(1) NULL DEFAULT 1,
  `isRetryAfterFailure` tinyint(1) NULL DEFAULT 0,
  `retryTimes` int(11) NULL DEFAULT 3,
  `isRandomIntervalTime` tinyint(1) NULL DEFAULT 1,
  `intervalTime` int(11) NULL DEFAULT 5,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sessions
-- ----------------------------
DROP TABLE IF EXISTS `sessions`;
CREATE TABLE `sessions`  (
  `uid` int(11) UNSIGNED NOT NULL,
  `tokenId` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`uid`) USING BTREE,
  CONSTRAINT `session_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for spiders
-- ----------------------------
DROP TABLE IF EXISTS `spiders`;
CREATE TABLE `spiders`  (
  `state` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `createTime` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `isMultiKey` tinyint(1) NULL DEFAULT NULL,
  `searchKey` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `selectedFilter` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `selectedCategory` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `taskCount` int(11) NULL DEFAULT NULL,
  `isCyclicMode` tinyint(1) NULL DEFAULT NULL,
  `waitTime` int(11) NULL DEFAULT NULL,
  `isToLike` tinyint(1) NULL DEFAULT NULL,
  `isToCollect` tinyint(1) NULL DEFAULT NULL,
  `isToFollow` tinyint(1) NULL DEFAULT NULL,
  `isComment` tinyint(1) NULL DEFAULT NULL,
  `commentMode` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
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
  `qrCodeState` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `secureSession` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `session` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `userId` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  PRIMARY KEY (`userId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `uid` int(11) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户编号',
  `uname` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名',
  `upwd` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '密码',
  `max_limit` int(11) NULL DEFAULT NULL COMMENT '爬虫数量限制',
  `is_admin` tinyint(1) NULL DEFAULT NULL COMMENT '是否为管理员',
  `is_disabled` tinyint(1) NULL DEFAULT NULL COMMENT '是否禁用',
  `is_wait` tinyint(1) NULL DEFAULT NULL COMMENT '登录是否等待',
  `wait_time` timestamp NULL DEFAULT NULL COMMENT '等待时间',
  `error` int(11) NULL DEFAULT NULL COMMENT '错误次数',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`uid`, `uname`) USING BTREE,
  INDEX `uid`(`uid`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users_config
-- ----------------------------
DROP TABLE IF EXISTS `users_config`;
CREATE TABLE `users_config`  (
  `uid` int(11) UNSIGNED NOT NULL,
  `id` int(11) NOT NULL,
  PRIMARY KEY (`uid`, `id`) USING BTREE,
  INDEX `c_id`(`id`) USING BTREE,
  CONSTRAINT `c_id` FOREIGN KEY (`id`) REFERENCES `config` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `c_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users_spiders
-- ----------------------------
DROP TABLE IF EXISTS `users_spiders`;
CREATE TABLE `users_spiders`  (
  `order` int(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `uid` int(11) UNSIGNED NOT NULL,
  `userId` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`order`) USING BTREE,
  INDEX `s_uid`(`uid`) USING BTREE,
  INDEX `s_userId`(`userId`) USING BTREE,
  CONSTRAINT `s_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `s_userId` FOREIGN KEY (`userId`) REFERENCES `spiders` (`userId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
