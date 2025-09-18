
#Arthur 2025.3.23 
2�Ż� ����������ƶȱȶ�
ALTER TABLE `m_app_match` ADD COLUMN `HIDE_REASON` varchar(256) NULL COMMENT '����ԭ��' AFTER `exception`;
ALTER TABLE `m_app_match` ADD COLUMN `HIDE_CONFIRM` varchar(2) NULL COMMENT '����ȷ�ϣ�0δȷ�ϣ�1��ȷ��' AFTER `exception`;

#Arthur 2025.4.10���½��㣩

2�Ż����£�
-- �ظ���USER_ID
delete from m_app_user where MAJUSER_ID in('6e6ce5ea36db4c9f812921bdb79aa1db','f077f8f579e84277bfd69f4e8a2ab500','4de3e139074b4e988619d68ef70871d0');

ALTER TABLE `m_app_user`  ADD UNIQUE INDEX(`USER_ID`);
ALTER TABLE `order_history`  ADD INDEX(`ORDER_ID`);
ALTER TABLE `m_match_settle` ADD COLUMN `RUN_TYPE` tinyint(2) NOT NULL DEFAULT 0 COMMENT '���㷽ʽ: 0 �ɽ��� �� 1 �½���' AFTER `GAME_TYPE`;


6�Ż����£�
ALTER TABLE `m_app_user`  ADD UNIQUE INDEX(`USER_ID`);
ALTER TABLE `order_history`  ADD INDEX(`ORDER_ID`);
ALTER TABLE `m_app_operation` ADD COLUMN `MATCH_ID` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT '������' AFTER `DESC`;
ALTER TABLE `m_match_settle` ADD COLUMN `RUN_TYPE` tinyint(2) NOT NULL DEFAULT 0 COMMENT '���㷽ʽ: 0 �ɽ��� �� 1 �½���' AFTER `STATUS`;
ALTER TABLE `m_app_order` CHANGE COLUMN `agent_code` `AGENT_CODE` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '����code';
ALTER TABLE `order_history` CHANGE COLUMN `bet_odds` `BET_ODDS` decimal(5, 2) NULL DEFAULT NULL;


#Arthur 2025.5.19 ���������������ID
2�Ż����£���ʵ�ʸ���ʱ��6.11��
ALTER TABLE `m_app_match` 
ADD COLUMN `HOST_TEAM_WEBID` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '����ID' AFTER `HIDE_REASON`,
ADD COLUMN `GUEST_TEAM_WEBID` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '�Ͷ�ID' AFTER `HOST_TEAM_WEBID`;


#Arthur 2025.6.4 ��֧��+�½���
5��okbet���£�
SET FOREIGN_KEY_CHECKS=0;
ALTER TABLE `m_agent` ADD COLUMN `AUTO_DEPOSIT` tinyint(4) NULL DEFAULT 0 AFTER `REMARK`;
ALTER TABLE `m_agent_new` ADD COLUMN `AUTO_DEPOSIT` tinyint(1) NULL DEFAULT 0 AFTER `MAC_LOGIN`;
ALTER TABLE `m_charge_apply` ADD COLUMN `PICTURE` varchar(256) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '��ֵͼƬ����' AFTER `REMARK`;
ALTER TABLE `m_app_operation` ADD COLUMN `MATCH_ID` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT '������' AFTER `DESC`;
ALTER TABLE `m_app_user` ADD UNIQUE INDEX `USER_ID`(`USER_ID`) USING BTREE;

ALTER TABLE `m_charge_apply` ADD COLUMN `USER_PRIMARY` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `REASON`;
ALTER TABLE `m_charge_apply` ADD COLUMN `P_REAL_NAME` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `USER_PRIMARY`;
ALTER TABLE `m_charge_apply` ADD COLUMN `P_PHONE` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL AFTER `P_REAL_NAME`;
ALTER TABLE `m_charge_apply` MODIFY COLUMN `STATUS` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT 'new' COMMENT '��������״̬' AFTER `CREATE_TIME`;

ALTER TABLE `m_app_bankcard` ADD COLUMN `PRIMARY_CARD` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Ĭ�����п�';
ALTER TABLE `m_app_bankcard` ADD COLUMN `CARD_ACCOUNT` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '' COMMENT '���п��˺�';
ALTER TABLE `m_app_bankcard` ADD COLUMN `IN_OUT` tinyint(3) UNSIGNED NOT NULL DEFAULT 0 COMMENT '���п����������� 0:���� 1:����';

ALTER TABLE `m_charge_apply` ADD INDEX `ix_m_charge_apply_USER_PRIMARY`(`USER_PRIMARY`) USING BTREE;
ALTER TABLE `m_match_settle` ADD COLUMN `RUN_TYPE` tinyint(2) NOT NULL DEFAULT 0 COMMENT '���㷽ʽ: 0 �ɽ��� �� 1 �½���' AFTER `STATUS`;
ALTER TABLE `order_history` ADD INDEX `ORDER_ID`(`ORDER_ID`) USING BTREE;

ALTER TABLE `m_app_order` CHANGE COLUMN `agent_code` `AGENT_CODE` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '����code';
ALTER TABLE `order_history` CHANGE COLUMN `bet_odds` `BET_ODDS` decimal(5, 2) NULL DEFAULT NULL;

SET FOREIGN_KEY_CHECKS=1;


===============================================================================================
TODO
#Arthur 5�Ż� ����������ƶȱȶ�
ALTER TABLE `m_app_match` ADD COLUMN `HIDE_REASON` varchar(256) NULL COMMENT '����ԭ��' AFTER `exception`;
ALTER TABLE `m_app_match` ADD COLUMN `HIDE_CONFIRM` varchar(2) NULL COMMENT '����ȷ�ϣ�0δȷ�ϣ�1��ȷ��' AFTER `exception`;

ALTER TABLE m_charge_apply ADD COLUMN OUT_ORDER_NO varchar(64) NULL COMMENT '֧�����Ķ�����';
ALTER TABLE m_charge_apply ADD COLUMN OUT_ORDER_ID varchar(64) NULL COMMENT '֧�����Ķ���ID';