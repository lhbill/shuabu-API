const axios = require('axios');
const { URLSearchParams } = require('url');
const moment = require('moment');

// 基础请求头（保留已补充的必传字段）
const headers = {
  'User-Agent': 'MiFit/6.12.0 (MCE16; Android 16; Density/1.5)',
  'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
  'app_name': 'com.xiaomi.hm.health',
  'Origin': 'https://user.zepp.com'
};

// 1. 从URL提取登录code（逻辑不变）
async function getCode(location) {
  const codePattern = /(?<=access=).*?(?=&)/;
  const match = location.match(codePattern);
  return match ? match[0] : null;
}

// 2. 登录核心函数（保留所有已修复逻辑：账号类型判断、双步请求、参数编码等）
async function login(account, password) {
  try {
    const isPhone = /^(1)\d{10}$/.test(account);
    const third_name = isPhone ? 'huami_phone' : 'huami';
    console.log('登录账号类型:', isPhone ? '手机号' : '邮箱');
    
    // 账号格式化+解码（修复逻辑不变）
    let formattedAccount = account;
    if (isPhone) {
      formattedAccount = '+86' + account.replace(/^\+86|^86/, '');
    }
    formattedAccount = decodeURIComponent(formattedAccount);
    console.log('最终原始账号:', formattedAccount);

    // 第一步：获取access code（URL编码+参数处理不变）
    const encodedAccountForUrl = encodeURIComponent(formattedAccount);
    const url1 = `https://api-user.zepp.com/registrations/${encodedAccountForUrl}/tokens`;
    const data1 = new URLSearchParams({
      client_id: 'HuaMi',
      name: formattedAccount,
      password: password,
      redirect_uri: 'https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html',
      token: 'access',
      country_code: 'CN',
      json_response: 'true',
      state: 'REDIRECTION'
    });

    console.log('第一步请求URL:', url1);
    console.log('第一步请求数据:', data1.toString());

    const response1 = await axios.post(url1, data1, {
      headers,
      maxRedirects: 0,
      validateStatus: status => status >= 200 && status < 400
    });

    console.log('第一步响应状态码:', response1.status);
    console.log('第一步响应头:', response1.headers);

    // 重定向头+响应体双处理（修复逻辑不变）
    let code = null;
    if (response1.headers.location) {
      code = await getCode(response1.headers.location);
      console.log('从重定向头获取code:', code);
    } else if (response1.status === 200 && response1.data?.access) {
      code = response1.data.access;
      console.log('从响应体获取code:', code);
    }

    if (!code) throw new Error('获取access code失败（账号/密码错误或参数异常）');

    // 第二步：获取loginToken和userId（参数不变）
    const url2 = 'https://account.zepp.com/v2/client/login';
    const data2 = new URLSearchParams({
      allow_registration: 'false',
      app_name: 'com.xiaomi.hm.health',
      app_version: '6.12.0',
      code: code,
      country_code: 'CN',
      device_id: 'fuck1069-2002-7869-0129-757geoi6sam1',
      device_model: 'android_phone',
      dn: 'account.zepp.com,api-user.zepp.com,api-mifit.zepp.com,api-watch.zepp.com,app-analytics.zepp.com,api-analytics.huami.com,auth.zepp.com',
      grant_type: 'access_token',
      source: 'com.xiaomi.hm.health',
      third_name: third_name
    });

    console.log('第二步请求URL:', url2);
    console.log('第二步请求数据:', data2.toString());

    const response2 = await axios.post(url2, data2, {
      headers,
      validateStatus: status => status >= 200 && status < 400
    });

    if (!response2.data?.token_info) throw new Error('未获取到token信息');

    const { login_token: loginToken, user_id: userId } = response2.data.token_info;
    if (!loginToken || !userId) throw new Error('token信息不完整');

    console.log('登录成功：loginToken=', loginToken, 'userId=', userId);
    return { loginToken, userId };
  } catch (error) {
    console.error('登录失败:', error.message);
    throw error;
  }
}

// 3. 获取appToken（逻辑不变）
async function getAppToken(loginToken) {
  try {
    const url = `https://account-cn.zepp.com/v1/client/app_tokens?app_name=com.xiaomi.hm.health&dn=api-user.zepp.com%2Capi-mifit.zepp.com%2Capp-analytics.zepp.com&login_token=${loginToken}`;
    console.log('获取appToken请求URL:', url);

    const response = await axios.get(url, { headers });
    if (!response.data?.token_info?.app_token) throw new Error('appToken获取失败');

    const appToken = response.data.token_info.app_token;
    console.log('获取appToken成功:', appToken);
    return appToken;
  } catch (error) {
    console.error('获取appToken失败:', error.message);
    throw error;
  }
}

// 4. 提交步数（保留修复逻辑，仅简化长字符串）
async function updateSteps(userId, appToken, steps) {
  try {
    const todayWithOffset = moment().add(8, 'hours').format('YYYY-MM-DD');
    console.log('当前日期:', todayWithOffset);
    console.log('目标步数:', steps);

    // 简化：用占位符替代冗长字符串，核心结构和替换逻辑不变
    const dataJson = `[
      {
        "data_hr": "[长字符串省略]",
        "date": "${todayWithOffset}",
        "data": [{"start":0,"stop":1439,"value":"[长字符串省略]","tz":32,"did":"DA932FFFFE8816E7","src":24}],
        "summary": "{\"v\":6,\"slp\":[长字符串省略],\"stp\":{\"ttl\":${steps},[长字符串省略]},\"goal\":8000,\"tz\":\"28800\"}",
        "source":24,
        "type":0
      }
    ]`;

    // 提交参数（逻辑不变）
    const url = `https://api-mifit-cn.zepp.com/v1/data/band_data.json?t=${Date.now()}`;
    const data = new URLSearchParams({
      userid: userId,
      last_sync_data_time: '1755407692',
      device_type: '0',
      last_deviceid: 'DA932FFFFE8816E7',
      data_json: dataJson
    });

    console.log('提交步数请求URL:', url);
    console.log('提交步数请求数据（简化）:', data.toString().slice(0, 100) + '...'); // 只打印前100字符避免冗余

    const response = await axios.post(url, data, {
      headers: { ...headers, apptoken: appToken },
      validateStatus: status => status >= 200 && status < 400
    });

    if (response.data.code !== 1) throw new Error(`提交失败: ${JSON.stringify(response.data)}`);
    console.log('步数提交成功！响应:', response.data);
    return response.data;
  } catch (error) {
    console.error('提交步数失败:', error.message);
    throw error;
  }
}

// 导出函数（供外部调用）
module.exports = { login, getAppToken, updateSteps };