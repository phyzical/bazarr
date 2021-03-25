import {
  faClock,
  faCloudUploadAlt,
  faDownload,
  faRecycle,
  faTrash,
  faUser,
} from "@fortawesome/free-solid-svg-icons";
import {
  FontAwesomeIcon,
  FontAwesomeIconProps,
} from "@fortawesome/react-fontawesome";
import moment from "moment";
import React, { FunctionComponent, useMemo } from "react";
import {
  OverlayTrigger,
  Popover,
  Spinner,
  SpinnerProps,
} from "react-bootstrap";

enum HistoryAction {
  Delete = 0,
  Download,
  Manual,
  Upgrade,
  Upload,
  Sync,
}

export const HistoryIcon: FunctionComponent<{
  action: number;
  title?: string;
}> = (props) => {
  const { action, title } = props;
  let icon = null;
  switch (action) {
    case HistoryAction.Delete:
      icon = faTrash;
      break;
    case HistoryAction.Download:
      icon = faDownload;
      break;
    case HistoryAction.Manual:
      icon = faUser;
      break;
    case HistoryAction.Sync:
      icon = faClock;
      break;
    case HistoryAction.Upgrade:
      icon = faRecycle;
      break;
    case HistoryAction.Upload:
      icon = faCloudUploadAlt;
      break;
  }
  if (icon) {
    return <FontAwesomeIcon title={title} icon={icon}></FontAwesomeIcon>;
  } else {
    return null;
  }
};

interface MessageIconProps extends FontAwesomeIconProps {
  messages: string[];
}

export const MessageIcon: FunctionComponent<MessageIconProps> = (props) => {
  const { messages, ...iconProps } = props;

  const popover = (
    <Popover hidden={messages.length === 0} id="overlay-icon">
      <Popover.Content>
        {messages.map((m) => (
          <li key={m}>{m}</li>
        ))}
      </Popover.Content>
    </Popover>
  );

  return (
    <OverlayTrigger overlay={popover}>
      <FontAwesomeIcon {...iconProps}></FontAwesomeIcon>
    </OverlayTrigger>
  );
};

export const LoadingIndicator: FunctionComponent<{
  animation?: SpinnerProps["animation"];
}> = ({ children, animation: style }) => {
  return (
    <div className="d-flex flex-column flex-grow-1 align-items-center py-5">
      <Spinner animation={style ?? "border"} className="mb-2"></Spinner>
      {children}
    </div>
  );
};

interface FormatterProps {
  format?: string;
  children: string | Date;
}

export const DateFormatter: FunctionComponent<FormatterProps> = ({
  children,
  format,
}) => {
  const result = useMemo(
    () => moment(children, format ?? "DD/MM/YYYY h:mm:ss").fromNow(),
    [children, format]
  );
  return <span>{result}</span>;
};

interface LanguageTextProps {
  text: Language;
  className?: string;
  long?: boolean;
}

export const LanguageText: FunctionComponent<LanguageTextProps> = ({
  text,
  className,
  long,
}) => {
  const result = useMemo(() => {
    let lang = text.code2;
    let hi = ":HI";
    let forced = ":Forced";
    if (long) {
      lang = text.name;
      hi = " HI";
      forced = " Forced";
    }

    let res = lang;
    if (text.hi) {
      res += hi;
    } else if (text.forced) {
      res += forced;
    }
    return res;
  }, [text, long]);
  return (
    <span title={text.name} className={className}>
      {result}
    </span>
  );
};

export * from "./async";
export * from "./buttons";
export * from "./ContentHeader";
export * from "./inputs";
export * from "./LanguageSelector";
export * from "./modals";
export * from "./SearchBar";
export * from "./tables";
