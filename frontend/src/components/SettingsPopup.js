import React, { useState, useRef, useEffect } from 'react';
import ReactDOM from 'react-dom';
import './SettingsPopup.css';
import { ReactComponent as PortraitIcon } from '../assets/icons/ic_portrait.svg';
import { ReactComponent as LandscapeIcon } from '../assets/icons/ic_landscape.svg';
import { ReactComponent as DurationIcon } from '../assets/icons/ic_duration.svg';
import { ReactComponent as EditIcon } from '../assets/icons/ic_edit.svg';

function SettingsPopup({
  aspectRatio,
  duration,
  noMusic,
  noCrowd,
  noCommentators,
  likeAnime,
  onAspectRatioChange,
  onDurationChange,
  onToggleMusic,
  onToggleCrowd,
  onToggleCommentators,
  onToggleLikeAnime,
  onClose,
  triggerRef
}) {
  const [activeSubmenu, setActiveSubmenu] = useState(null);
  const popupRef = useRef(null);
  const [position, setPosition] = useState({ bottom: 0, right: 0 });

  // Calculate position based on trigger button
  useEffect(() => {
    if (triggerRef?.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      // Position popup aligned with right edge of button
      setPosition({
        bottom: window.innerHeight - rect.top + 10,
        right: window.innerWidth - rect.right - 10,
      });
    }
  }, [triggerRef]);

  // Close popup when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popupRef.current && !popupRef.current.contains(event.target) &&
          triggerRef?.current && !triggerRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose, triggerRef]);

  const handleOrientationSelect = (orientation) => {
    onAspectRatioChange(orientation);
    setActiveSubmenu(null);
  };

  const handleDurationSelect = (dur) => {
    onDurationChange(dur);
    setActiveSubmenu(null);
  };

  const popupContent = (
    <div
      className="settings-popup"
      ref={popupRef}
      style={{
        position: 'fixed',
        bottom: `${position.bottom}px`,
        right: `${position.right}px`,
      }}
    >
      {/* Orientation option */}
      <div
        className="popup-option"
        onMouseEnter={() => setActiveSubmenu('orientation')}
      >
        <div className="option-left">
          {aspectRatio === 'portrait' ? <PortraitIcon /> : <LandscapeIcon />}
          <span className="option-label">Orientation</span>
        </div>
        <div className="option-right">
          <span className="option-value">
            {aspectRatio === 'portrait' ? 'Portrait' : 'Landscape'}
          </span>
          <span className="option-arrow">›</span>
        </div>

        {/* Orientation submenu */}
        {activeSubmenu === 'orientation' && (
          <div className="submenu">
            <div
              className="submenu-item"
              onClick={() => handleOrientationSelect('portrait')}
            >
              <PortraitIcon />
              <span>Portrait</span>
              {aspectRatio === 'portrait' && <span className="checkmark">✓</span>}
            </div>
            <div
              className="submenu-item"
              onClick={() => handleOrientationSelect('landscape')}
            >
              <LandscapeIcon />
              <span>Landscape</span>
              {aspectRatio === 'landscape' && <span className="checkmark">✓</span>}
            </div>
          </div>
        )}
      </div>

      {/* Duration option */}
      <div
        className="popup-option"
        onMouseEnter={() => setActiveSubmenu('duration')}
      >
        <div className="option-left">
          <DurationIcon />
          <span className="option-label">Duration</span>
        </div>
        <div className="option-right">
          <span className="option-value">{duration}s</span>
          <span className="option-arrow">›</span>
        </div>

        {/* Duration submenu */}
        {activeSubmenu === 'duration' && (
          <div className="submenu">
            <div
              className="submenu-item"
              onClick={() => handleDurationSelect(10)}
            >
              <DurationIcon />
              <span>10s</span>
              {duration === 10 && <span className="checkmark">✓</span>}
            </div>
            <div
              className="submenu-item"
              onClick={() => handleDurationSelect(15)}
            >
              <DurationIcon />
              <span>15s</span>
              {duration === 15 && <span className="checkmark">✓</span>}
            </div>
          </div>
        )}
      </div>

      {/* Modifiers option */}
      <div
        className="popup-option"
        onMouseEnter={() => setActiveSubmenu('modifiers')}
      >
        <div className="option-left">
          <EditIcon />
          <span className="option-label">Prompt modifiers</span>
        </div>
        <div className="option-right">
          <span className="option-arrow">›</span>
        </div>

        {/* Modifiers submenu */}
        {activeSubmenu === 'modifiers' && (
          <div className="submenu">
            <div
              className="submenu-item"
              onClick={onToggleMusic}
            >
              <span>No music</span>
              {noMusic && <span className="checkmark">✓</span>}
            </div>
            <div
              className="submenu-item"
              onClick={onToggleCrowd}
            >
              <span>No crowd</span>
              {noCrowd && <span className="checkmark">✓</span>}
            </div>
            <div
              className="submenu-item"
              onClick={onToggleCommentators}
            >
              <span>No commentators</span>
              {noCommentators && <span className="checkmark">✓</span>}
            </div>
            <div
              className="submenu-item"
              onClick={onToggleLikeAnime}
            >
              <span>Like anime</span>
              {likeAnime && <span className="checkmark">✓</span>}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return ReactDOM.createPortal(popupContent, document.body);
}

export default SettingsPopup;
