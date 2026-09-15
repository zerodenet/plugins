type HostContract = {
  surfaces: Record<string, string>;
  capabilities: Record<string, string>;
};

// These labels describe host-owned protocol keys. They never override
// publisher-supplied product metadata, and unknown keys remain untranslated.
const hostContracts: Record<string, HostContract> = {
  zboard: {
    surfaces: {
      public: '公开前台',
      account: '用户前台',
      admin: '管理后台',
    },
    capabilities: {
      'zboard.ui.page.v1': '展示插件页面',
      'zboard.config.v1': '管理自身配置',
      'zboard.identity.provider.v1': '验证第三方身份',
      'zboard.storage.v1': '读写自身私有数据',
    },
  },
};

const hosts: Record<string, string> = {
  zboard: 'ZBoard',
  'znet-sink': 'ZNet Sink',
};

const channels: Record<string, string> = {
  stable: '正式版',
  rc: '候选版',
  dev: '开发预览版',
};

export const hostDescription = (key: string) => hosts[key];
export const channelDescription = (key: string) => channels[key];
export const surfaceDescription = (host: string, key: string) => hostContracts[host]?.surfaces[key];
export const capabilityDescription = (host: string, key: string) => hostContracts[host]?.capabilities[key];
