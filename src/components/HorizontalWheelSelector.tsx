import { motion } from 'motion/react';
import { useLang } from '../i18n';

interface HorizontalWheelSelectorProps {
  items: string[];
  selectedItem: string;
  onSelect: (item: string) => void;
}

export function HorizontalWheelSelector({ items, selectedItem, onSelect }: HorizontalWheelSelectorProps) {
  const selectedIndex = items.findIndex(item => item === selectedItem);
  const { t } = useLang();

  const handleWheel = (e: React.WheelEvent) => {
    // Check for either horizontal or vertical wheel movement
    const delta = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
    
    if (Math.abs(delta) < 15) return;
    
    const direction = delta > 0 ? 1 : -1;
    const nextIndex = selectedIndex + direction;
    
    if (nextIndex >= 0 && nextIndex < items.length) {
      onSelect(items[nextIndex]);
    }
  };

  return (
    <div 
      onWheel={handleWheel}
      className="relative w-[700px] h-10 flex items-center justify-center overflow-visible select-none"
    >
      <div className="relative w-full h-full">
        {items.map((item, index) => {
          const distance = index - selectedIndex;
          const absDistance = Math.abs(distance);
          const isActive = selectedItem === item;

          // Limit render to items near active
          if (absDistance > 6) return null;

          // Horizontal layout math
          const translateX = distance * 150;
          
          // Downward curving (like a drum)
          const translateY = Math.pow(absDistance, 1.4) * 3;
          
          // Scaling and styling
          const scale = 1 - (absDistance * 0.08);
          const opacity = isActive ? 1 : Math.max(0, 0.4 - (absDistance * 0.1));

          return (
            <motion.div
              key={item}
              onClick={() => onSelect(item)}
              className="absolute h-full cursor-pointer flex items-center justify-center"
              style={{
                left: '50%',
                marginLeft: '-80px', // slightly wider layout for longer translated tags
                width: '160px',
                transformOrigin: 'center top'
              }}
              animate={{
                x: translateX,
                y: translateY,
                scale,
                opacity,
              }}
              transition={{ type: 'spring', stiffness: 350, damping: 30 }}
            >
              <div
                className={`whitespace-nowrap transition-colors duration-300 ${
                  isActive 
                    ? 'text-[15px] font-bold text-zinc-900 tracking-tight' 
                    : 'text-[14px] font-[500] text-zinc-400 hover:text-zinc-600'
                }`}
              >
                {t(item)}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  );
}
