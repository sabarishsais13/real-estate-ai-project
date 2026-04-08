import argparse
import cv2
import numpy as np


def clamp(value, minimum, maximum):
    """Clamp a value between minimum and maximum."""
    return max(minimum, min(value, maximum))


class InteractivePanoramaViewer:
    """Interactive viewer that supports panning and cursor-centered zoom."""

    def __init__(self, image_path, window_name="Panorama Viewer", window_size=(1280, 720)):
        self.window_name = window_name
        self.window_width, self.window_height = window_size

        self.image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if self.image is None:
            raise ValueError(f"Could not load image: {image_path}")

        self.image_height, self.image_width = self.image.shape[:2]

        self.zoom = 1.0
        self.target_zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.zoom_step = 0.1
        self.zoom_smooth = 0.2

        # For horizontal panning on the panorama
        self.center_x = self.image_width // 2
        self.center_y = self.image_height // 2

        # Cursor position inside the display window
        self.cursor_x = self.window_width // 2
        self.cursor_y = self.window_height // 2

        # Mouse state flags
        self.is_dragging = False
        self.last_mouse_x = None
        self.pan_speed = 1.0

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)
        cv2.setMouseCallback(self.window_name, self._mouse_callback)

    def _window_to_image_coords(self, x, y, zoom):
        """Convert window pixel coordinates to original image coordinates."""
        view_w = int(self.window_width / zoom)
        view_h = int(self.window_height / zoom)
        image_x = self.center_x - view_w // 2 + int(x / zoom)
        image_y = self.center_y - view_h // 2 + int(y / zoom)
        return image_x, image_y

    def _update_target_center_for_zoom(self, cursor_x, cursor_y, new_zoom):
        """Re-center the viewport so the cursor point stays fixed during zoom."""
        old_zoom = self.zoom
        old_view_w = int(self.window_width / old_zoom)
        old_view_h = int(self.window_height / old_zoom)
        new_view_w = int(self.window_width / new_zoom)
        new_view_h = int(self.window_height / new_zoom)

        # Find the image point currently under the cursor.
        image_x = self.center_x - old_view_w // 2 + int(cursor_x / old_zoom)
        image_y = self.center_y - old_view_h // 2 + int(cursor_y / old_zoom)

        # Compute new center so that the same image point maps to the same cursor location.
        self.center_x = int(image_x - cursor_x / new_zoom + new_view_w / 2)
        self.center_y = int(image_y - cursor_y / new_zoom + new_view_h / 2)

        # For panorama, wrap horizontally and clamp vertically.
        self.center_x %= self.image_width
        self.center_y = clamp(self.center_y, new_view_h // 2, self.image_height - new_view_h // 2)

    def _mouse_callback(self, event, x, y, flags, param):
        """Track cursor movement, scroll events, and drag-based panning."""
        self.cursor_x = x
        self.cursor_y = y

        if event == cv2.EVENT_MOUSEMOVE and self.is_dragging:
            if self.last_mouse_x is not None:
                dx = x - self.last_mouse_x
                self.center_x -= int(dx * self.pan_speed / self.zoom)
                self.center_x %= self.image_width
            self.last_mouse_x = x

        elif event == cv2.EVENT_LBUTTONDOWN:
            self.is_dragging = True
            self.last_mouse_x = x

        elif event == cv2.EVENT_LBUTTONUP:
            self.is_dragging = False
            self.last_mouse_x = None

        elif event == cv2.EVENT_MOUSEWHEEL:
            # Positive flags for wheel forward, negative for wheel backward
            direction = 1 if flags > 0 else -1
            self._change_zoom(direction, x, y)

        elif event == cv2.EVENT_MOUSEHWHEEL:
            # Optional horizontal wheel event (some platforms support this).
            direction = -1 if flags > 0 else 1
            self._change_zoom(direction, x, y)

    def _change_zoom(self, direction, cursor_x, cursor_y):
        """Adjust the target zoom and keep the cursor focus stable."""
        next_zoom = clamp(self.target_zoom + direction * self.zoom_step, self.min_zoom, self.max_zoom)
        if next_zoom == self.target_zoom:
            return

        self.target_zoom = next_zoom
        self._update_target_center_for_zoom(cursor_x, cursor_y, self.target_zoom)

    def _draw_overlay(self, frame):
        """Draw zoom level, controls, and boundary helper overlays."""
        text = f"Zoom: {self.zoom:.2f}x | +/- or mouse wheel | Drag horizontally to pan"
        cv2.rectangle(frame, (10, 10), (self.window_width - 10, 38), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        # Draw a subtle center cursor target to help users see zoom anchor.
        cv2.circle(frame, (self.cursor_x, self.cursor_y), 8, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.circle(frame, (self.cursor_x, self.cursor_y), 3, (0, 255, 0), -1)

    def _render_frame(self):
        """Crop and rescale the panorama region for the current zoom and pan state."""
        # Smoothly interpolate zoom for a fluid experience.
        if abs(self.zoom - self.target_zoom) > 0.001:
            self.zoom += (self.target_zoom - self.zoom) * self.zoom_smooth
        else:
            self.zoom = self.target_zoom

        view_w = int(self.window_width / self.zoom)
        view_h = int(self.window_height / self.zoom)

        view_w = clamp(view_w, 1, self.image_width)
        view_h = clamp(view_h, 1, self.image_height)

        self.center_y = clamp(self.center_y, view_h // 2, self.image_height - view_h // 2)

        x1 = self.center_x - view_w // 2
        x2 = x1 + view_w
        y1 = self.center_y - view_h // 2
        y2 = y1 + view_h

        if y1 < 0:
            y1 = 0
            y2 = view_h
        if y2 > self.image_height:
            y2 = self.image_height
            y1 = self.image_height - view_h

        if x1 < 0 or x2 > self.image_width:
            # Wrap horizontally for a seamless 360-panorama.
            x1_mod = x1 % self.image_width
            x2_mod = x2 % self.image_width
            if x1_mod < x2_mod:
                viewport = self.image[y1:y2, x1_mod:x2_mod]
            else:
                left_slice = self.image[y1:y2, x1_mod:]
                right_slice = self.image[y1:y2, :x2_mod]
                viewport = np.concatenate((left_slice, right_slice), axis=1)
        else:
            viewport = self.image[y1:y2, x1:x2]

        frame = cv2.resize(viewport, (self.window_width, self.window_height), interpolation=cv2.INTER_LINEAR)
        self._draw_overlay(frame)
        return frame

    def run(self):
        """Open the viewer window and handle keyboard input."""
        while True:
            frame = self._render_frame()
            cv2.imshow(self.window_name, frame)

            key = cv2.waitKey(20) & 0xFF
            if key == 27:  # ESC
                break
            if key in (ord('+'), ord('=')):
                self._change_zoom(1, self.cursor_x, self.cursor_y)
            elif key == ord('-'):
                self._change_zoom(-1, self.cursor_x, self.cursor_y)
            elif key == ord('0'):
                self.target_zoom = 1.0
                self._update_target_center_for_zoom(self.cursor_x, self.cursor_y, self.target_zoom)

            # Keyboard panning fallback.
            elif key == ord('a') or key == 81:  # left arrow
                self.center_x -= int(40 / self.zoom)
                self.center_x %= self.image_width
            elif key == ord('d') or key == 83:  # right arrow
                self.center_x += int(40 / self.zoom)
                self.center_x %= self.image_width

        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Interactive 360° panorama viewer with zoom and pan.")
    parser.add_argument("image_path", help="Path to the stitched panorama image")
    parser.add_argument("--width", type=int, default=1280, help="Viewer window width")
    parser.add_argument("--height", type=int, default=720, help="Viewer window height")
    args = parser.parse_args()

    viewer = InteractivePanoramaViewer(args.image_path, window_size=(args.width, args.height))
    viewer.run()


if __name__ == "__main__":
    main()
