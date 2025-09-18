
#Arthur 2025.3.23 
2号机 爬虫球队相似度比对
ALTER TABLE `m_app_match` ADD COLUMN `HIDE_REASON` varchar(256) NULL COMMENT '隐藏原因' AFTER `exception`;
ALTER TABLE `m_app_match` ADD COLUMN `HIDE_CONFIRM` varchar(2) NULL COMMENT '隐藏确认：0未确认，1已确认' AFTER `exception`;

#Arthur 2025.4.10（新结算）

2号机更新：
-- 重复的USER_ID
delete from m_app_user where MAJUSER_ID in('6e6ce5ea36db4c9f812921bdb79aa1db','f077f8f579e84277bfd69f4e8a2ab500','4de3e139074b4e988619d68ef70871d0');

ALTER TABLE `m_app_user`  ADD UNIQUE INDEX(`USER_ID`);
ALTER TABLE `order_history`  ADD INDEX(`ORDER_ID`);
ALTER TABLE `m_match_settle` ADD COLUMN `RUN_TYPE` tinyint(2) NOT NULL DEFAULT 0 COMMENT '结算方式: 0 旧结算 ， 1 新结算' AFTER `GAME_TYPE`;


6号机更新：
ALTER TABLE `m_app_user`  ADD UNIQUE INDEX(`USER_ID`);
ALTER TABLE `order_history`  ADD INDEX(`ORDER_ID`);
ALTER TABLE `m_app_operation` ADD COLUMN `MATCH_ID` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT '比赛号' AFTER `DESC`;
ALTER TABLE `m_match_settle` ADD COLUMN `RUN_TYPE` tinyint(2) NOT NULL DEFAULT 0 COMMENT '结算方式: 0 旧结算 ， 1 新结算' AFTER `STATUS`;
ALTER TABLE `m_app_order` CHANGE COLUMN `agent_code` `AGENT_CODE` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '代理code';
ALTER TABLE `order_history` CHANGE COLUMN `bet_odds` `BET_ODDS` decimal(5, 2) NULL DEFAULT NULL;


#Arthur 2025.5.19 爬虫赛事增加球队ID
2号机更新：（实际更新时间6.11）
ALTER TABLE `m_app_match` 
ADD COLUMN `HOST_TEAM_WEBID` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '主队ID' AFTER `HIDE_REASON`,
ADD COLUMN `GUEST_TEAM_WEBID` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '客队ID' AFTER `HOST_TEAM_WEBID`;


#Arthur 2025.6.4 新支付+新结算
5号okbet更新：
SET FOREIGN_KEY_CHECKS=0;
ALTER TABLE `m_agent` ADD COLUMN `AUTO_DEPOSIT` tinyint(4) NULL DEFAULT 0 AFTER `REMARK`;
ALTER TABLE `m_agent_new` ADD COLUMN `AUTO_DEPOSIT` tinyint(1) NULL DEFAULT 0 AFTER `MAC_LOGIN`;
ALTER TABLE `m_charge_apply` ADD COLUMN `PICTURE` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '充值图片名称' AFTER `REMARK`;
ALTER TABLE `m_app_operation` ADD COLUMN `MATCH_ID` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT '比赛号' AFTER `DESC`;
ALTER TABLE `m_app_user` ADD UNIQUE INDEX `USER_ID`(`USER_ID`) USING BTREE;

ALTER TABLE `m_charge_apply` ADD COLUMN `USER_PRIMARY` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `REASON`;
ALTER TABLE `m_charge_apply` ADD COLUMN `P_REAL_NAME` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `USER_PRIMARY`;
ALTER TABLE `m_charge_apply` ADD COLUMN `P_PHONE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `P_REAL_NAME`;
ALTER TABLE `m_charge_apply` MODIFY COLUMN `STATUS` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT 'new' COMMENT '订单处理状态' AFTER `CREATE_TIME`;

ALTER TABLE `m_app_bankcard` ADD COLUMN `PRIMARY_CARD` tinyint(1) NOT NULL DEFAULT 0 COMMENT '默认银行卡';
ALTER TABLE `m_app_bankcard` ADD COLUMN `CARD_ACCOUNT` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '' COMMENT '银行卡账号';
ALTER TABLE `m_app_bankcard` ADD COLUMN `IN_OUT` tinyint(3) UNSIGNED NOT NULL DEFAULT 0 COMMENT '银行卡进出款类型 0:进款 1:出款';

ALTER TABLE `m_charge_apply` ADD INDEX `ix_m_charge_apply_USER_PRIMARY`(`USER_PRIMARY`) USING BTREE;
ALTER TABLE `m_match_settle` ADD COLUMN `RUN_TYPE` tinyint(2) NOT NULL DEFAULT 0 COMMENT '结算方式: 0 旧结算 ， 1 新结算' AFTER `STATUS`;
ALTER TABLE `order_history` ADD INDEX `ORDER_ID`(`ORDER_ID`) USING BTREE;

ALTER TABLE `m_app_order` CHANGE COLUMN `agent_code` `AGENT_CODE` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '代理code';
ALTER TABLE `order_history` CHANGE COLUMN `bet_odds` `BET_ODDS` decimal(5, 2) NULL DEFAULT NULL;

SET FOREIGN_KEY_CHECKS=1;


===============================================================================================
TODO
#Arthur 5号机 爬虫球队相似度比对
ALTER TABLE `m_app_match` ADD COLUMN `HIDE_REASON` varchar(256) NULL COMMENT '隐藏原因' AFTER `exception`;
ALTER TABLE `m_app_match` ADD COLUMN `HIDE_CONFIRM` varchar(2) NULL COMMENT '隐藏确认：0未确认，1已确认' AFTER `exception`;

ALTER TABLE m_charge_apply ADD COLUMN OUT_ORDER_NO varchar(64) NULL COMMENT '支付中心订单号';
ALTER TABLE m_charge_apply ADD COLUMN OUT_ORDER_ID varchar(64) NULL COMMENT '支付中心订单ID';