import { Component, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

interface Props {
  children: ReactNode;
}
interface State {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: "" };

  static getDerivedStateFromError(error: unknown): State {
    return {
      hasError: true,
      message: error instanceof Error ? error.message : "渲染过程中发生未知错误",
    };
  }

  componentDidCatch(error: unknown) {
    // eslint-disable-next-line no-console
    console.error("Dashboard render error:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-banner" role="alert">
          <AlertTriangle size={18} />
          <span style={{ flex: 1 }}>
            诊断面板渲染失败：{this.state.message}。请重新选择案例或刷新页面。
          </span>
          <button className="retry-button" onClick={() => this.setState({ hasError: false, message: "" })}>
            重置面板
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
