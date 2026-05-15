import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, QrCode, CheckCircle2 } from 'lucide-react';
import { TOP_LEVEL_GROUPS, CATEGORY_MAP, TopLevelGroup, Category } from '../data/entities';
import { useLang } from '../i18n';

export function ContactModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const { t } = useLang();
  
  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative w-full max-w-sm bg-white rounded-[24px] shadow-2xl p-8 overflow-hidden"
          >
            <button onClick={onClose} className="absolute top-4 right-4 p-2 text-zinc-400 hover:text-zinc-800 transition-colors rounded-full hover:bg-zinc-100">
              <X className="w-5 h-5" />
            </button>
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4">
                <QrCode className="w-6 h-6" />
              </div>
              <h3 className="text-[18px] font-bold text-zinc-900 mb-1">{t('contact.title')}</h3>
              <p className="text-[13px] text-zinc-500 mb-6 text-center">{t('contact.desc')}</p>
              
              <div className="w-48 h-48 bg-zinc-50 border border-zinc-200 rounded-[16px] flex items-center justify-center p-4 mb-6">
                 {/* Placeholder for real QR code */}
                 <div className="w-full h-full border-2 border-dashed border-zinc-300 rounded-[8px] flex items-center justify-center flex-col gap-2 text-zinc-400">
                   <QrCode className="w-8 h-8 opacity-50" />
                   <span className="text-[12px] font-medium text-center">Your QR Code<br/>Here</span>
                 </div>
              </div>

              <div className="text-[13px] font-medium text-zinc-600 bg-zinc-50 px-4 py-2 rounded-full border border-zinc-200">
                ID: Robotics_101
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

export function SubmitModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const { t } = useLang();
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success'>('idle');
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    topGroup: '硬件' as TopLevelGroup,
    category: '整机平台' as Category,
    description: '',
    link: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('submitting');
    
    // 这里填写未来你在此项目关联的 GitHub 仓库地址
    const REPO_URL = "https://github.com/SunYue98/RoboIndex"; 
    
    const issueTitle = `[新增收录 | New Entity] ${formData.name}`;
    const issueBody = `### 实体信息 (Entity Information)
- **名称 (Name)**: ${formData.name}
- **机构 (Company)**: ${formData.company || 'N/A'}
- **领域 (Sector)**: ${formData.topGroup}
- **分类 (Category)**: ${formData.category}
- **链接 (Link)**: ${formData.link || 'N/A'}

### 描述与参数 (Description / Specs)
${formData.description || '无详细描述 (No description provided)'}

---
*此 Issue 由系统前端自动生成，请管理员审核后加入 data.json。*`;

    const encodedTitle = encodeURIComponent(issueTitle);
    const encodedBody = encodeURIComponent(issueBody);
    
    // 模拟一下等待感，然后跳转 GitHub
    setTimeout(() => {
      // 在新标签页打开 GitHub Issue 页面
      window.open(`${REPO_URL}/issues/new?title=${encodedTitle}&body=${encodedBody}`, '_blank');
      
      setStatus('success');
      setTimeout(() => {
        onClose();
        setTimeout(() => {
          setStatus('idle');
          setFormData({
            name: '', company: '', topGroup: '硬件', category: '整机平台', description: '', link: ''
          });
        }, 300);
      }, 2000);
    }, 800);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={status === 'submitting' ? undefined : onClose}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative w-full max-w-lg bg-white rounded-[24px] shadow-2xl p-8 overflow-hidden"
          >
            {status !== 'submitting' && (
              <button onClick={onClose} className="absolute top-4 right-4 p-2 text-zinc-400 hover:text-zinc-800 transition-colors rounded-full hover:bg-zinc-100 z-10">
                <X className="w-5 h-5" />
              </button>
            )}

            {status === 'success' ? (
              <div className="flex flex-col items-center justify-center py-12">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", bounce: 0.5 }}
                >
                  <CheckCircle2 className="w-16 h-16 text-emerald-500 mb-4" />
                </motion.div>
                <h3 className="text-[20px] font-bold text-zinc-900 mb-2">{t('submit.success.title')}</h3>
                <p className="text-[14px] text-zinc-500 text-center" dangerouslySetInnerHTML={{ __html: t('submit.success.desc') }} />
              </div>
            ) : (
              <div className="flex flex-col h-full max-h-[80vh]">
                <h3 className="text-[20px] font-bold text-zinc-900 mb-1">{t('submit.title')}</h3>
                <p className="text-[13px] text-zinc-500 mb-6">{t('submit.desc')}</p>
                
                <form onSubmit={handleSubmit} className="flex flex-col gap-4 overflow-y-auto pr-2 pb-2">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] font-bold text-zinc-700">{t('submit.form.name')}</label>
                    <input 
                      required
                      type="text" 
                      value={formData.name}
                      onChange={e => setFormData({...formData, name: e.target.value})}
                      className="w-full px-4 py-2.5 bg-zinc-50 border border-zinc-200 rounded-[12px] text-[14px] focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:bg-white transition-all"
                    />
                  </div>
                  
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] font-bold text-zinc-700">{t('submit.form.company')}</label>
                    <input 
                      type="text" 
                      value={formData.company}
                      onChange={e => setFormData({...formData, company: e.target.value})}
                      className="w-full px-4 py-2.5 bg-zinc-50 border border-zinc-200 rounded-[12px] text-[14px] focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:bg-white transition-all"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[13px] font-bold text-zinc-700">{t('submit.form.master')}</label>
                      <select 
                        value={formData.topGroup}
                        onChange={e => {
                          const topGroup = e.target.value as TopLevelGroup;
                          setFormData({
                            ...formData, 
                            topGroup, 
                            category: CATEGORY_MAP[topGroup][0] 
                          });
                        }}
                        className="w-full px-4 py-2.5 bg-zinc-50 border border-zinc-200 rounded-[12px] text-[14px] focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:bg-white transition-all cursor-pointer"
                      >
                        {TOP_LEVEL_GROUPS.map(g => <option key={g} value={g}>{t(g)}</option>)}
                      </select>
                    </div>

                    <div className="flex flex-col gap-1.5">
                      <label className="text-[13px] font-bold text-zinc-700">{t('submit.form.category')}</label>
                      <select 
                        value={formData.category}
                        onChange={e => setFormData({...formData, category: e.target.value as Category})}
                        className="w-full px-4 py-2.5 bg-zinc-50 border border-zinc-200 rounded-[12px] text-[14px] focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:bg-white transition-all cursor-pointer"
                      >
                        {CATEGORY_MAP[formData.topGroup].map(c => <option key={c} value={c}>{t(c)}</option>)}
                      </select>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] font-bold text-zinc-700">{t('submit.form.link')}</label>
                    <input 
                      type="url" 
                      value={formData.link}
                      onChange={e => setFormData({...formData, link: e.target.value})}
                      className="w-full px-4 py-2.5 bg-zinc-50 border border-zinc-200 rounded-[12px] text-[14px] focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:bg-white transition-all"
                      placeholder="https://..." 
                    />
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-[13px] font-bold text-zinc-700">{t('submit.form.specs')}</label>
                    <textarea 
                      rows={3}
                      value={formData.description}
                      onChange={e => setFormData({...formData, description: e.target.value})}
                      className="w-full px-4 py-2.5 bg-zinc-50 border border-zinc-200 rounded-[12px] text-[14px] focus:outline-none focus:ring-2 focus:ring-zinc-400 focus:bg-white transition-all resize-none"
                    />
                  </div>

                  <button 
                    disabled={status === 'submitting'}
                    type="submit" 
                    className="mt-4 w-full py-3 bg-zinc-900 hover:bg-zinc-800 text-white font-bold rounded-[12px] transition-all focus:outline-none focus:ring-4 focus:ring-zinc-200 flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                  >
                    {status === 'submitting' ? (
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      t('submit.btn.submit')
                    )}
                  </button>
                </form>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
