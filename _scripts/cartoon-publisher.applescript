property runnerCommand : __RUNNER__

on chooseCartoonImage()
	return choose file with prompt "Choose the finished cartoon to publish" of type {"public.image"}
end chooseCartoonImage

on promptTitle(defaultTitle)
	repeat
		set answer to display dialog "Cartoon title" default answer defaultTitle buttons {"Cancel", "Continue"} default button "Continue" cancel button "Cancel" with title "Publish Cartoon"
		set titleText to text returned of answer
		if titleText is not "" then return titleText
	end repeat
end promptTitle

on promptAltDescription()
	repeat
		set answer to display dialog "Briefly describe the scene and its words for people using screen readers." default answer "" buttons {"Cancel", "Continue"} default button "Continue" cancel button "Cancel" with title "Image description"
		set altText to text returned of answer
		if altText is not "" then return altText
	end repeat
end promptAltDescription

on confirmPublish(draft)
	set answer to display dialog "Publish “" & (cartoonTitle of draft) & "” on ajin.im?" & return & return & (imageDescription of draft) buttons {"Cancel", "Publish"} default button "Publish" cancel button "Cancel" with title "Publish Cartoon"
	return button returned of answer is "Publish"
end confirmPublish

on notifyProgress(draft, stageText)
	set publishStage of draft to stageText
	display notification stageText with title "Publish Cartoon"
end notifyProgress

on runPublisher(draft)
	set commandText to runnerCommand & " --image " & quoted form of (imagePath of draft) & " --title " & quoted form of (cartoonTitle of draft) & " --alt " & quoted form of (imageDescription of draft)
	with timeout of 3600 seconds
		return do shell script commandText
	end timeout
end runPublisher

on showResult(liveURL)
	set answer to display dialog "Your cartoon is live." & return & return & liveURL buttons {"Done", "View cartoon"} default button "View cartoon" with title "Published"
	if button returned of answer is "View cartoon" then open location liveURL
end showResult

on run
	try
		set selectedImage to chooseCartoonImage()
		set sourcePath to POSIX path of selectedImage
		set suggestedTitle to do shell script runnerCommand & " --suggest-title " & quoted form of sourcePath
		set draft to {imagePath:sourcePath, cartoonTitle:promptTitle(suggestedTitle), imageDescription:promptAltDescription(), publishing:false, publishStage:"Ready"}
		if confirmPublish(draft) then
			set publishing of draft to true
			notifyProgress(draft, "Publishing. A result will appear after the live page is checked.")
			set liveURL to runPublisher(draft)
			showResult(liveURL)
		end if
	on error errorMessage number errorNumber
		if errorNumber is not -128 then display dialog errorMessage buttons {"OK"} default button "OK" with title "Publishing needs attention"
	end try
end run
